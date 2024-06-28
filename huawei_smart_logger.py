import requests
import paho.mqtt.client as mqtt
import logging
import json
import re
import logging
import time
import os
from random import randrange
import datetime

from const import IS_CONTAINER, VERSION, SLEEP_INTERVAL, ENTITIES

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

if (IS_CONTAINER):
    HUAWEI_HOST = os.getenv("HUAWEI_HOST","https://192.168.50.38")
    HUAWEI_PASSWORD=os.getenv("HUAWEI_PASSWORD","")
    HUAWEI_USERNAME=os.getenv("HUAWEI_USERNAME","admin")
    MQTT_HOST = os.getenv("MQTT_HOST","earthquake.832-5.jp")
    MQTT_PASSWORD=os.getenv("MQTT_PASSWORD","")
    MQTT_USERNAME=os.getenv("MQTT_USERNAME","japan")   

class HuaweiSmartLoggerSensor:
    def __init__(self, name_constant):
        name_replace=name_constant
        name_object=ENTITIES[name_constant]
        self.name = f"huawei_smart_logger_{name_replace}"
        self.device_class = name_object['type'],
        self.unit_of_measurement = name_object['unit'],
        test = name_object.get('attribute')
        if (test != None):
           self.state_class = name_object['attribute']
        else:
            self.state_class = "measurement"
        self.state_topic = f"homeassistant/sensor/huawei_smart_logger_{name_replace}/state"
        self.unique_id = f"huawei_smart_logger_{name_replace}"
        self.device = {
            "identifiers": [f"huawei_smart_logger_{name_replace}"][0],
            "name": f"Huawei Smart Logger For {name_replace}",
        }

    def to_json(self):
        return {
            "name": self.name,
            "device_class": self.device_class[0],
            "unit_of_measurement": self.unit_of_measurement[0],
            "state_class": self.state_class,
            "state_topic": self.state_topic,
            "unique_id": self.unique_id,
            "device": self.device
        }


def initialize():
    logger = logging.getLogger(__name__)
    logger.info(f"Initialization starting...")
    print("Initialization starting...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
    client.connect(MQTT_HOST, 1883)

    for entity in ENTITIES:
        huawei_smart_logger_sensor=HuaweiSmartLoggerSensor(entity)
        # Convert dictionary to JSON string
        serialized_message = json.dumps(huawei_smart_logger_sensor.to_json())
        print(f"Sending sensor -> {serialized_message}")
        logger.info(f"Sending sensor -> {serialized_message}")
        print(f"entity: homeassistant/sensor/huawei_smart_logger_{entity}/config")
        client.publish(f"homeassistant/sensor/huawei_smart_logger_{entity}/config", payload=serialized_message, qos=0, retain=True)
   
        
    client.disconnect()
    logger.info(f"Initialization complete...")
    print("Initialization complete...")

def request_and_publish():

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
    logger = logging.getLogger(__name__)

    # Perform login and save the cookies
    login_url = f"{HUAWEI_HOST}/action/login"

    login_data = {
        'langlist': 0,
        'usrname': HUAWEI_USERNAME,
        'string': HUAWEI_PASSWORD,
        'vercodeinput': '',
        'login': 'Log+In'
    }

    session = requests.Session()
    session.post(login_url, data=login_data, verify=False)

    # Get CSRF token and save it to a file
    csrf_url = f"{HUAWEI_HOST}/js/csrf.jst"
    response = session.get(csrf_url, verify=False)
    token_match = re.search(r'tokenObj.value = \"([^\"]+)\"', response.text)
    csrf_token = token_match.group(1) if token_match else None

    # Use the token to make the next request and process the response
    info_url = f"{HUAWEI_HOST}/get_set_page_info.asp?type=88"
    headers = {'x-csrf-token': csrf_token}

    response = session.get(info_url, headers=headers, verify=False)
    response_lines = response.text.split('|')

    for line in response_lines:

        element = line.split('~')
        if len(element) < 7: 
            continue
        
        entity= element[2].lower()
        if entity == "(null)":
            continue

        entity = re.sub(r'\s+', '_', entity)
        entity = re.sub(r'\'', '', entity)
        entity = re.sub(r'/', '', entity)
        value = element[7]

        print(f"{entity} -> {value}")
        client.connect(MQTT_HOST, 1883)
        client.publish(f"homeassistant/sensor/huawei_smart_logger_{entity}/state", payload=value, qos=0, retain=False)    
        client.disconnect()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info(f"I am huawei_smart_logger running version {VERSION}")
    print(f"I am huawei_smart_logger running version {VERSION}")
    initialize()

    while True:
        request_and_publish()
        logger.info(f"It is {datetime.datetime.now()} .. I am sleeping for {SLEEP_INTERVAL}")
        print(f"It is {datetime.datetime.now()} ... I am sleeping for {SLEEP_INTERVAL}")
        time.sleep(SLEEP_INTERVAL)