import json
import re
import signal
import time
from types import FrameType
from typing import Any, NoReturn

import paho.mqtt.client as mqtt
import requests
import urllib3
from paho.mqtt.enums import CallbackAPIVersion

from ..config import Settings, settings
from ..const import ENTITIES, VERSION
from ..logging import configure_logging, get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AVAILABILITY_TOPIC = "huawei/available"
logger = get_logger(__name__)


class HuaweiSmartLoggerSensor:
    def __init__(self, entity_name: str) -> None:
        entity = ENTITIES[entity_name]
        self.name = f"huawei_smart_logger_{entity_name}"
        self.device_class = entity["type"]
        self.unit_of_measurement = entity["unit"]
        self.state_class = entity.get("attribute", "measurement")
        self.state_topic = f"homeassistant/sensor/huawei_smart_logger_{entity_name}/state"
        self.unique_id = f"huawei_smart_logger_{entity_name}"
        self.device = {
            "identifiers": [self.unique_id],
            "name": f"Huawei Smart Logger For {entity_name}",
        }

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "device_class": self.device_class,
            "unit_of_measurement": self.unit_of_measurement,
            "state_class": self.state_class,
            "state_topic": self.state_topic,
            "availability_topic": AVAILABILITY_TOPIC,
            "payload_available": "online",
            "payload_not_available": "offline",
            "unique_id": self.unique_id,
            "device": self.device,
        }


def on_mqtt_connect(
    client: mqtt.Client,
    _userdata: Any,
    _flags: Any,
    reason_code: Any,
    _properties: Any,
) -> None:
    if reason_code == 0:
        client.publish(AVAILABILITY_TOPIC, payload="online", qos=1, retain=True)


def create_mqtt_client(config: Settings) -> mqtt.Client:
    client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id="huawei_smart_logger",
    )
    client.username_pw_set(config.mqtt_username, config.mqtt_password)
    client.will_set(AVAILABILITY_TOPIC, payload="offline", qos=1, retain=True)
    client.on_connect = on_mqtt_connect
    return client


def initialize(client: mqtt.Client) -> None:
    logger.info("Initialization starting")
    for entity_name in ENTITIES:
        sensor = HuaweiSmartLoggerSensor(entity_name)
        topic = f"homeassistant/sensor/huawei_smart_logger_{entity_name}/config"
        payload = json.dumps(sensor.to_json())
        logger.info("Publishing discovery config to %s", topic)
        try:
            result = client.publish(topic, payload=payload, qos=2, retain=True)
            result.wait_for_publish()
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error("Failed to queue discovery config for %s: %s", entity_name, result.rc)
        except Exception:
            logger.exception("Error publishing discovery config for %s", entity_name)
    logger.info("Initialization complete")


def request_and_publish(client: mqtt.Client, config: Settings) -> None:
    login_url = f"{config.huawei_host}/action/login"
    login_data = {
        "langlist": 0,
        "usrname": config.huawei_username,
        "string": config.huawei_password,
        "vercodeinput": "",
        "login": "Log+In",
    }

    with requests.Session() as session:
        session.post(login_url, data=login_data, verify=False, timeout=30).raise_for_status()
        csrf_url = f"{config.huawei_host}/js/csrf.jst"
        response = session.get(csrf_url, verify=False, timeout=30)
        response.raise_for_status()
        token_match = re.search(r'tokenObj.value = "([^"]+)"', response.text)
        csrf_token = token_match.group(1) if token_match else None

        info_url = f"{config.huawei_host}/get_set_page_info.asp?type=88"
        response = session.get(
            info_url,
            headers={"x-csrf-token": csrf_token},
            verify=False,
            timeout=30,
        )
        response.raise_for_status()

    for line in response.text.split("|"):
        element = line.split("~")
        if len(element) < 8:
            continue

        entity_name = element[2].lower()
        if entity_name == "(null)":
            continue
        entity_name = re.sub(r"\s+", "_", entity_name)
        entity_name = re.sub(r"'", "", entity_name)
        entity_name = re.sub(r"/", "_", entity_name)
        value = element[7]
        topic = f"homeassistant/sensor/huawei_smart_logger_{entity_name}/state"

        logger.info("Publishing %s -> %s", entity_name, value)
        try:
            result = client.publish(topic, payload=value, qos=2, retain=False)
            result.wait_for_publish()
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error("Failed to queue state for %s: %s", entity_name, result.rc)
        except Exception:
            logger.exception("Error publishing state for %s", entity_name)


def handle_sigterm(_signum: int, _frame: FrameType | None) -> NoReturn:
    raise SystemExit(0)


def main() -> None:
    configure_logging()
    logger.info("Starting Huawei Smart Logger %s", VERSION)
    signal.signal(signal.SIGTERM, handle_sigterm)
    client = create_mqtt_client(settings)

    try:
        try:
            client.connect(settings.mqtt_host, settings.mqtt_port)
        except Exception:
            logger.exception("Error connecting to MQTT broker")
        client.loop_start()
        initialize(client)

        while True:
            try:
                request_and_publish(client, settings)
            except Exception:
                logger.exception("Polling cycle failed")
            logger.info("Sleeping for %s seconds", settings.sleep_interval)
            time.sleep(settings.sleep_interval)
    finally:
        try:
            result = client.publish(AVAILABILITY_TOPIC, payload="offline", qos=1, retain=True)
            result.wait_for_publish(timeout=5)
        except Exception:
            logger.exception("Error publishing shutdown availability")
        try:
            client.disconnect()
        except Exception:
            logger.exception("Error disconnecting from MQTT broker")
        client.loop_stop()