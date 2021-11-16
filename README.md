NOTES: changes: app_config, docker-compose files (kafka outside ref link and lab9 as well)


# MicroService 

This application is about a sales transaction of a store. There are two event types that are online sales and in-store sales.

############### MANUAL #############

Requirement for VM:
  - at least 2GB of memory, Ubuntu 18.04 LTS . Make sure you setup a DNS Name for your VM
  - all the ssh (port 22) and connections are opened for port: 9092 (Kafka), 3306 (MySQL), 8080 (Receiver), 8090 (Storage), 8100 (Processing), 8200 (Audit)
  - Docker installed (Step 1 and Step 2 in this link https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04 )
  - Docker Compose installed https://docs.docker.com/compose/install/  (without needing sudo)
  - MYSQL connector installed (To create and drop tables) pip install mysql-connector-python-rf

After get into the machine, do:
  1. git pull (prefered) or git clone the repo. 
     You will get files as the TREE below. Our services include Receiver, Storage, Processing, Audit
  2. change `app_conf.yml` information in 4 services folder and `\development\docker-compose.yml` according to your needs
  3. cd to each dir of 4 services and run `docker build -t audit_log:latest` for example to create images
     These will build 4 images that have all required modules in `requirements.txt` and running your `app.py`
  4. After building 4 images, cd to development directory and do `docker-compose up -d` 
     Now when doing `docker ps -a`, you should see all container is running with app.py running
     (If you got an error that container is not up, you should run this cmd again without `-d` to see the logs
  5. cd into Storage directory and create table `python create_tables_mysql_kafka.py`
     If you want to drop the table do `python drop_tables_mysql_kafka.py`
  6. Now you can test by open 4 browers to run the services, for example: `<DNS name>:8080/ui` for Receiver service (note there is /ui at the end) or use jmeter to test
  TroubleShooting: Storage service may not always successfully connect to Kafka -> Stop the Storage container only and bring docker-compose up agian.
 
 Other usefull commands:
  - docker logs <container_id> : to see logs for container when the app.py is running. Add `-f` to follow the logs 
  - docker volume ls 
  - docker volume rm $(docker volume ls) : This will remove all the volume including caches for the database
  - docker system prune -a : This will delete all unused services in docker except docker volumn
  
########## BACKEND TREE INCLUDES ##################
```
├── audit_log
│   ├── Dockerfile
│   ├── app.py
│   ├── app_conf.yml
│   ├── log_conf.yml
│   ├── openapi.yml
│   └── requirements.txt
├── deployment  (## To makes docker containers base on the images mentioned in docker-compose.yml)
│   └── docker-compose.yml
├── processing
│   ├── Dockerfile
│   ├── app.py
│   ├── app_conf.yml
│   ├── log_conf.yml
│   ├── openapi.yml
│   └── requirements.txt
├── receiver
│   ├── Dockerfile
│   ├── app.py
│   ├── app_conf.yml
│   ├── log_conf.yml
│   ├── openapi.yml
│   └── requirements.txt
└── storage
    ├── Dockerfile
    ├── app.py
    ├── app_conf.yml
    ├── base.py
    ├── create_tables_mysql_kafka.py
    ├── drop_tables_mysql_kafka.py
    ├── instore_sales.py
    ├── log_conf.yml
    ├── online_sales.py
    ├── openapi.yml
    └── requirements.txt
  ```
