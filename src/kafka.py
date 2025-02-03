import os
from dotenv import load_dotenv
load_dotenv()
from kafka import KafkaProducer
import json

KAFKA_SERVER = os.getenv('KAFKA_SERVER')
producer = KafkaProducer(
    bootstrap_servers= KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)