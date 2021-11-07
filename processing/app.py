from datetime import datetime
import connexion
import json
import requests, yaml, logging, logging.config, uuid, datetime
from flask import Response
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin       

YAML_FILENAME = 'openapi.yml'
YAML_LOACTION = './'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# def get_stats():
#     logger.info("Request has started")
#     try:
#         with open('data.json', 'r') as f: #!!!! WHY THIS IS NOT WORKING
#             logger.info("Hello 1")
#             data=  json.loads(f.read()) 
#             logger.info("Hello 2", data)
#             logger.debug("Loaded statistics: {}".format(json.load(f)))
#             logger.info("Hello 3")
#             logger.info("get_stats request has been compelted")
#             return data,200
#     except: #If the file doesn’t exist
#         logger.error("Statistic file cannot be found!")
#         return "Statistics not exist", 404

def get_stats():
    logger.info("Request has started")
    try:
        with open(app_config['datastore']['filename'],'r') as file:
            file_data = file.read()
            logger.debug("Loaded statistics: {}".format(json.loads(file_data)))
            logger.info("get_stats request has been compelted")
            return json.loads(file_data),200
    except:
        logger.error("Statistic file cannot be found!")
        return "Statistics not exist", 404

def populate_stats():
    """ Periodically update stats """
    logger.info("periodic processing has started. Received event get_stats request")
    
    "Read in the current statistics from the JSON file (filename defined in your configuration)"
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)    
    except:
        "If the file doesn’t yet exist, use default values for the stats"
        with open(app_config['datastore']['filename'],'w') as file:
            #! Is this work without quoute "num_instore_sales"
            file.write(json.dumps({"num_instore_sales": 0, "max_instore_qty": 0,"num_online_sales": 0,"max_online_qty": 0,"last_updated": "2016-08-29T09:12:33Z"}))

    "Get the current datetime"
    now = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%dT%H:%M:%SZ")

    "Query the two GET endpoints from your Data Store Service to get all new events from the last datetime you requested them (from your statistics) to the current datetime"
    # 'last_updated' is written into json in the calculation below
    instore_request = requests.get(app_config['get_instore_sales']['url']+stats['last_updated'])
    online_request = requests.get(app_config['get_online_sales']['url']+stats['last_updated'])
    if  instore_request.status_code != 200:
        logger.error("ERROR ON Receiving data for instore.")
    else:
        logger.info("Successfully received instore.")
    if online_request.status_code != 200:
        logger.error("ERROR ON Receiving data for online.")
    else:
        logger.info("Successfully received online.")
    #Based on the new events from the Data Store Service
    instore_data = json.loads(instore_request.content)
    online_data = json.loads(instore_request.content)
    print("Hello instore", instore_data)
    print("Hello online", online_data)
    num_instore = len(instore_data) + stats["num_instore_sales"]
    num_online = len(online_data) + stats["num_online_sales"]
    max_instore_qty = max(max([x['bill_amount']['quantity'] for x in instore_data], default=0), stats["max_instore_qty"])
    max_online_qty = max(max([x['bill_amount']['quantity'] for x in instore_data], default=0), stats["max_online_qty"])
    data_obj = {"num_instore_sales": num_instore, "max_instore_qty": max_instore_qty,"num_online_sales": num_online,"max_online_qty": max_online_qty,"last_updated":now}
    with open(app_config['datastore']['filename'],'w') as file:
        file.write(json.dumps(data_obj))
    logger.debug("Successfully saved the new stats: {}".format(data_obj))

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir=YAML_LOACTION)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(YAML_FILENAME,
            strict_validation=True,
            validate_responses=True)    

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)