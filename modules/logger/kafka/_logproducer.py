import os
from kafka import KafkaProducer

# TOPIC_NAME = 'udaconnectlogs'
# KAFKA_SERVER = 'localhost:9092'
TOPIC_NAME = os.environ["KAFKA_TOPIC"]
KAFKA_SERVER = os.environ["KAFKA_SERVER"] + ':' + os.environ["KAFKA_PORT"]

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

producer.send(TOPIC_NAME, b'Kya baat hai KAFKA ki')
producer.flush()