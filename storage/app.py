import connexion
from connexion import NoContent
from flask import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import datetime, yaml, logging, logging.config, json, time
from instore_sales import InstoreSales
from online_sales import OnlineSales
import mysql.connector
from pykafka.common import OffsetType
from threading import Thread
from pykafka import KafkaClient
from sqlalchemy import and_
#pip install swagger-ui-bundle
#pip install mysql-connector-python
#pip install kafka-python
#pip install pykafka


with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    host = app_config["datastore"]["hostname"]
    logger.info(f"Connecting to DB. Hostname {host}, Port: 3306")
    

DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_instore_sales(start_timestamp, end_timestamp):
    "Gets new instore_sales event data after timestamp"
    session=DB_SESSION()
    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") 
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ") # Storage Service endpoints before only take a single timestamp, so the Processing won't know the end time 9*3
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ") # Storage Service endpoints before only take a single timestamp, so the Processing won't know the end time 9*3
    # transactions= session.query(InstoreSales).filter(InstoreSales.date_created >= timestamp_datetime)
    transactions = session.query(InstoreSales).filter( and_(InstoreSales.date_created >= start_timestamp_datetime, InstoreSales.date_created < end_timestamp_datetime))
    trans_list = []
    for tran in transactions:
        trans_list.append(tran.to_dict())
    session.close()

    logger.info("Query for Instore Sales after %s returns %d results" %(start_timestamp, len(trans_list)))
    
    return trans_list, 200  

def get_online_sales(start_timestamp, end_timestamp):
    "Gets new instore_sales event data after timestamp"
    session=DB_SESSION()
    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ") # Storage Service endpoints before only take a single timestamp, so the Processing won't know the end time 9*3
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ") # Storage Service endpoints before only take a single timestamp, so the Processing won't know the end time 9*3
    # transactions= session.query(OnlineSales).filter(OnlineSales.date_created >= timestamp_datetime)
    transactions = session.query(OnlineSales).filter( and_(OnlineSales.date_created >= start_timestamp_datetime, OnlineSales.date_created < end_timestamp_datetime))
    trans_list = []
    for tran in transactions:
        trans_list.append(tran.to_dict())
    session.close()

    logger.info("Query for Online Sales after %s returns %d results" %(start_timestamp, len(trans_list)))
    
    return trans_list, 200


def instore_sales(body):
    # auto_uuid = str(uuid.uuid4())
    session = DB_SESSION()
    instore_entry= InstoreSales(body['product_id'],
                    body['store_id'],
                    body['customer_id'],
                    body['sales_date'],
                    body['bill_amount']['quantity'],
                    body['bill_amount']['unit_price'])
    session.add(instore_entry)
    unq_id = body['product_id']

    logger.debug(f'Stored event instore_sales request with a unique id of {unq_id}')

    session.commit()
    session.close()

    #//return NoContent, 201 #Remove the previous POST API endpoints as new events will now be received through messages from Kafka.
    

def online_sales(body):

    session = DB_SESSION()

    online_entry = OnlineSales(body['product_id'],
                    body['customer_id'],
                    body['delivery_info'],
                    body['sales_date'],
                    body['bill_amount']['quantity'],
                    body['bill_amount']['unit_price'])

    unq_id = body['product_id']
    session.add(online_entry )

    logger.debug(f'Stored event online_sales request with a unique id of {unq_id}')

    session.commit()
    session.close()

    #//return NoContent, 201 #Remove the  POST API endpoints as new events will now be received through messages from Kafka.

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                        app_config["events"]["port"]) 
    # client = KafkaClient(hosts=hostname)
    # topic = client.topics[str.encode(app_config["events"]["topic"])]

    max_retry =app_config["connecting_kafka"]["retry_count_max"]
    retry_count = 0
    while retry_count < max_retry:
        logger.info(f"Connecting to Kafka and the current retry count is {retry_count + 1}")
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            retry_count = max_retry
        except:
            logger.error("Cannot Connect to Kafka. The connection failed")
            time.sleep(app_config["connecting_kafka"]["time_sleep"])
            retry_count += 1


    # Create a consume on a consumer group, that only reads new messages \
    # (uncommitted messages) when the service re-starts (i.e., it doesn't 
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                            reset_offset_on_start=False, 
                                            auto_offset_reset=OffsetType.LATEST)
    
    # This is blocking - it will wait for a new message
    for msg in consumer:
        try:
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            logger.info("Message: %s" % msg)

            payload = msg["payload"]

            if msg["type"] == "instore": #Change this to your event type - Get this from the openapi.yml line 13 `/sales/instore` so event type is `instore`
                # Store the event1 (i.e., the payload) to the DB
                instore_sales(payload)
                
            elif msg["type"] == "online": # Change this to your event type 
                #Store the event2 (i.e., the payload) to the DB
                online_sales(payload)

            # Commit the new message as being read
            consumer.commit_offsets()
        except:
            logger.error("Something is wrong. Cannot Store in DB table")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", 
            strict_validation=True, 
            validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)