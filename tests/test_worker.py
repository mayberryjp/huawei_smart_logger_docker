from unittest.mock import MagicMock, patch

from huawei_smart_logger.config import Settings
from huawei_smart_logger.workers.smart_logger import (
    AVAILABILITY_TOPIC,
    HuaweiSmartLoggerSensor,
    create_mqtt_client,
    on_mqtt_connect,
)


def test_discovery_config_includes_availability() -> None:
    config = HuaweiSmartLoggerSensor("load_power").to_json()

    assert config["availability_topic"] == AVAILABILITY_TOPIC
    assert config["payload_available"] == "online"
    assert config["payload_not_available"] == "offline"


def test_create_mqtt_client_sets_retained_last_will() -> None:
    settings = Settings(mqtt_username="logger", mqtt_password="secret")
    client = MagicMock()

    with patch("huawei_smart_logger.workers.smart_logger.mqtt.Client", return_value=client):
        result = create_mqtt_client(settings)

    assert result is client
    client.username_pw_set.assert_called_once_with("logger", "secret")
    client.will_set.assert_called_once_with(
        AVAILABILITY_TOPIC,
        payload="offline",
        qos=1,
        retain=True,
    )


def test_connect_publishes_online_status() -> None:
    client = MagicMock()

    on_mqtt_connect(client, None, None, 0, None)

    client.publish.assert_called_once_with(
        AVAILABILITY_TOPIC,
        payload="online",
        qos=1,
        retain=True,
    )