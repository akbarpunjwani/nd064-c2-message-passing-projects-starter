import os
import sys
from kafka import KafkaConsumer

# 'udaconnectlogs'
TOPIC_NAME = os.environ["KAFKA_TOPIC"]
KAFKA_SERVER = os.environ["KAFKA_SERVER"] + ':' + os.environ["KAFKA_PORT"]

print('Initiating the consumer for ',TOPIC_NAME,' from KAFKA SERVER ',KAFKA_SERVER)
isConsumerReady=0

while isConsumerReady == 0:
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME, 
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='smallest'
            )
        print('KAFKA consumer is READY!')
        isConsumerReady=1
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")
        print()
        isConsumerReady=0

print('Starting the loop to iteratively consume messages',TOPIC_NAME,' from KAFKA SERVER ',KAFKA_SERVER)
for message in consumer:
    try:
        val=str(message.value)
        print(val[2:len(val)-1])
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")
        print()

print('ENDING the consumer for ',TOPIC_NAME,' from KAFKA SERVER ',KAFKA_SERVER)