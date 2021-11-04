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
db_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}" )
#change events.instore_sales and events.online_sales to corresponding db and tables 

db_cursor.execute(f'''
    CREATE TABLE {db_name}.instore_sales 
    (id INT NOT NULL AUTO_INCREMENT, 
    product_id VARCHAR(250) NOT NULL,
    store_id VARCHAR(4) NOT NULL,
    customer_id VARCHAR(10) NOT NULL,
    sales_date VARCHAR(250) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(6,2) NOT NULL,
    date_created VARCHAR(100) NOT NULL,
    CONSTRAINT instore_sales_pk PRIMARY KEY (id))
    ''')

db_cursor.execute(f'''
    CREATE TABLE {db_name}.online_sales 
    (id INT NOT NULL AUTO_INCREMENT, 
    product_id VARCHAR(250) NOT NULL,
    customer_id VARCHAR(10) NOT NULL,
    delivery_info VARCHAR(250) NOT NULL,
    sales_date VARCHAR(250) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(6,2) NOT NULL,
    date_created VARCHAR(100) NOT NULL,
    CONSTRAINT online_sales_pk PRIMARY KEY (id))
    ''')
    
db_conn.commit()
db_conn.close()
