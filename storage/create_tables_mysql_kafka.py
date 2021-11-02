import mysql.connector
#pip install mysql-connector-python

db_conn = mysql.connector.connect(host="microservice-henrik.eastus.cloudapp.azure.com",port="3306", user="root", password="Password")
db_cursor = db_conn.cursor()

db_cursor.execute("CREATE DATABASE IF NOT EXISTS events" )
#change events.instore_sales and events.online_sales to corresponding db and tables 

db_cursor.execute('''
    CREATE TABLE events.instore_sales 
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

db_cursor.execute('''
    CREATE TABLE events.online_sales 
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