from datetime import datetime
import connexion
import json
import requests, yaml, logging, logging.config, uuid, datetime, os
from flask import Response
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin       

YAML_FILENAME = 'openapi.yml'   
YAML_LOCATION = './'

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

logger = logging.getLogger('basimembership_validateogger')

logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

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

    "Get the current datetime"
    current_timestamp = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%dT%H:%M:%SZ")
    
    "Read in the current statistics from the JSON file (filename defined in your configuration)"
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)    
    except:
        "If the file doesn’t yet exist, use default values for the stats"
        with open(app_config['datastore']['filename'],'w') as file:
            #! Is this work without quoute "num_personal_info_sales"
            # file.write(json.dumps({"num_personal_info_sales": 0, "max_personal_info_readings": 0,"num_membership_validate_sales": 0,"max_membership_validate_readings": 0,"last_updated": "2016-08-29T09:12:33Z"}))
            file.write(json.dumps(
                {"num_personal_info_readings": 0, "max_personal_info_readings": 0, "num_membership_validate_readings": 0, "max_membership_validate_readings": 0,
                    "last_updated": "2016-08-29T09:12:33Z"}))

    "Query the two GET endpoints from your Data Store Service to get all new events from the last datetime you requested them (from your statistics) to the current datetime"
    # 'last_updated' is written into json in the calculation below
    # personal_info_request = requests.get(app_config['get_instore_sales']['url']+stats['last_updated'])
    # membership_validate_request = requests.get(app_config['get_online_sales']['url']+stats['last_updated'])
    last_updated = stats['last_updated']
    personal_info_request = requests.get(app_config['eventstore']['url'] + "/readings/personal_information?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp)
    membership_validate_request = requests.get(app_config['eventstore']['url'] + "/readings/start_end_date?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp)
    if  personal_info_request.status_code != 200:
        logger.error("ERROR ON Receiving data for instore.")
    else:
        logger.info("Successfully received instore.")
    if membership_validate_request.status_code != 200:
        logger.error("ERROR ON Receiving data for online.")
    else:
        logger.info("Successfully received online.")
    #Based on the new events from the Data Store Service
    personal_info_data = json.loads(personal_info_request.content)
    membership_validate_data = json.loads(membership_validate_request.content)
    num_personal_info = len(personal_info_data) + stats["num_personal_info_readings"]
    num_membership_validate = len(membership_validate_data) + stats["num_membership_validate_readings"]
    max_personal_info_readings = max(max([x['age'] for x in personal_info_data], default=0), stats["max_personal_info_readings"])
    max_membership_validate_readings = max(max([x['duration_months'] for x in membership_validate_data], default=0), stats["max_membership_validate_readings"])
    data_obj = {"num_personal_info_readings": num_personal_info, "max_personal_info_readings": max_personal_info_readings,"num_membership_validate_readings": num_membership_validate,"max_membership_validate_readings": max_membership_validate_readings,"last_updated":current_timestamp}
    with open(app_config['datastore']['filename'],'w') as file:
        file.write(json.dumps(data_obj))
    logger.debug("Successfully saved the new stats: {}".format(data_obj))

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir=YAML_LOCATION)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(YAML_FILENAME,
            strict_validation=True,
            validate_responses=True)    

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)