import connexion
from connexion import NoContent
import json, logging.config, requests, logging, yaml
import os
import uuid
from flask import Response
from pykafka import KafkaClient
from datetime import datetime
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

def get_instore_sales(index):
    """ Get instore Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    my_ls = []
    logger.info("Retrieving BP at index %d" % index)
    try:
        print('1')
        for msg in consumer:
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str)
        # Find the event at the index you want and # return code 200
        # i.e., return event, 200
            if msg["type"] == "instore":
                my_ls.append(msg['payload'])
        if len(my_ls) > index:
            event = my_ls[index]
            return event, 200

    except:
        logger.error("No more messages found")
    logger.error("Could not find BP at index %d" % index)
    return { "message": "Not Found"}, 404

def get_online_sales(index):
    """ Get online Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    my_ls = []
    logger.info("Retrieving BP at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str)
        # Find the event at the index you want and # return code 200
        # i.e., return event, 200
            if msg["type"] == "online":
                my_ls.append(msg['payload'])
        if len(my_ls) > index:
            event = my_ls[index]
            return event, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find BP at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
# CORS(app.app)
# app.app.config['CORS_HEADERS'] = 'Content-Type'
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

# app.add_api("openapi.yml",strict_validation=True, validate_responses=True)
app.add_api("openapi.yml", 
            base_path="/audit_log", 
            strict_validation=True, 
            validate_responses=True) 

if __name__ == "__main__":
    app.run(port=8200, debug=True)
