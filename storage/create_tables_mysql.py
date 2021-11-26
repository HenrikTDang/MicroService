import mysql.connector
import yaml
#pip install mysql-connector-python

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host= app_config["datastore"]["hostname"],
                                    port= app_config["datastore"]["port"], 
                                    user= app_config["datastore"]["user"], 
                                    password= app_config["datastore"]["password"])
db_cursor = db_conn.cursor()

db_name= app_config["datastore"]["db"]
db_cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name) )

db_cursor.execute('''
    CREATE TABLE events.personal_information
    (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    member_id VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    address VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    date_created VARCHAR(100) NOT NULL)
    ''')

db_cursor.execute('''
    CREATE TABLE events.membership_validity
    (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    member_id VARCHAR(250) NOT NULL,
    location_id VARCHAR(250) NOT NULL,
    start_date VARCHAR(100) NOT NULL,
    duration_months INTEGER NOT NULL,
    date_created VARCHAR(100) NOT NULL)
    ''')
    
db_conn.commit()
db_conn.close()