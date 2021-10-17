import os
from kafka.admin import KafkaAdminClient, NewTopic

TOPIC_NAME = os.environ["KAFKA_TOPIC"]
KAFKA_SERVER = os.environ["KAFKA_SERVER"] + ':' + os.environ["KAFKA_PORT"]

admin_client = KafkaAdminClient(
    api_version=(2,0,2),
    bootstrap_servers=[KAFKA_SERVER]
    # client_id='modules_logger_1'
)

topic_list = []
topic_list.append(NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1))
print('trying to create topic')
admin_client.create_topics(new_topics=topic_list, validate_only=False)
print('TOPIC CREATED',topic_list)