import mysql.connector 

db_conn = mysql.connector.connect(host="microservice-henrik.eastus.cloudapp.azure.com", user="user", 
password="Password", database="events") 
db_cursor = db_conn.cursor()
db_cursor.execute(''' DROP TABLE online_sales, instore_sales ''') 
db_conn.commit() 
db_conn.close()
