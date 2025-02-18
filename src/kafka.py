import os
from dotenv import load_dotenv
load_dotenv()
from kafka import KafkaProducer
import json
import time

KAFKA_SERVER = os.getenv('KAFKA_SERVER')
def get_kafka_producer(retries=5, delay=5):
    for _ in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            print(f"Kafka not ready, retrying in {delay} seconds... Error: {e}")
            time.sleep(delay)
    raise Exception("Kafka not available after retries")

producer = get_kafka_producer()