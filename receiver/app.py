import connexion
from connexion import NoContent
import json, logging.config, requests, logging, yaml, time
import os
import uuid
from flask import Response
from pykafka import KafkaClient
from datetime import datetime
import datetime


# with open('log_conf.yml', 'r') as f: 
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

# with open('app_conf.yml', 'r') as f: 
#     app_config = yaml.safe_load(f.read())

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

hostname = "%s:%d" % (app_config["events"]["hostname"],
                    app_config["events"]["port"]) 
max_retry =app_config["connecting_kafka"]["retry_count_max"]
retry_count = 0
while retry_count < max_retry:
    logger.info(f"Connecting to Kafka and the current retry count is {retry_count + 1}")
    try:
        client = KafkaClient(hosts= hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        retry_count = max_retry
    except:
        logger.error("Cannot Connect to Kafka. The connection failed")
        time.sleep(app_config["connecting_kafka"]["time_sleep"])
        retry_count += 1

# def get_instore_sales(timestamp):
#     logger.info("Received event get_instore_sales request {}".format(uuid.uuid4()))
#     request = requests.get(app_config['get_instore_sales']['url']+"?timestamp="+json.dumps(timestamp))
#     logger.info("Returned event get_instore_sales response  {} with status {}".format(uuid.uuid4(),request.status_code))
#     return Response(response=request.content,status=200,headers={'Content-type': 'application/json'})

# def get_online_sales(timestamp):
#     logger.info("Received event get_groups request {}".format(uuid.uuid4()))
#     request = requests.get(app_config['get_online_sales']['url']+"?timestamp="+json.dumps(timestamp))
#     logger.info("Returned event get_online_sales response  {} with status {}".format(uuid.uuid4(),request.status_code))
#     return Response(response=request.content,status=200,headers={'Content-type': 'application/json'})


def instore_sales(body):
    logger.info(f"Received event instore_sales request with a unique id of {body['product_id']}")
    #// response = requests.post(app_config['instore_sales']['url'], json=body)                 ##LAB5
    #// logger.info(f"Returned event instore_sales response(ID: {body['product_id']}) witt status {response.status_code}")
    #// return NoContent, response.status_code

    # client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}') 
    # topic = client.topics[str.encode(app_config["events"]["topic"])] 
    # producer = topic.get_sync_producer()

    msg = { "type": "instore",   #event type Get this from the openapi.yml line 13 `/sales/instore` so event type is `instore`
        "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body }  
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return msg_str, 201 #! You will need to hard-code your status code to 201 since you will no longer get it from the response of the requests.post call


def online_sales(body):
    #// headers = {"content-type":"application/json"}
    logger.info (f"Received event online_sales request with a unique id of {body['product_id']}")
    #// response = requests.post(app_config['online_sales']['url'], json=body,  headers=headers)    ##LAB5
    #// logger.info(f"Returned event online_sales response(ID: {body['product_id']}) witt status {response.status_code}")
    #// return NoContent, response.status_code
    # client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}') 
    # topic = client.topics[str.encode(app_config["events"]["topic"])] 
    # producer = topic.get_sync_producer()

    msg = { "type": "online",   #event type
        "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body }  
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return msg_str, 201 #! You will need to hard-code your status code to 201 since you will no longer get it from the response of the requests.post call

app = connexion.FlaskApp(__name__, specification_dir='')
# app.add_api("openapi.yml", 
#             strict_validation=True, 
#             validate_responses=True)
app.add_api("openapi.yml", 
            base_path="/receiver", 
            strict_validation=True, 
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
