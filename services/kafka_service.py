# kafka_service.py

from kafka import KafkaConsumer, KafkaProducer
import json
from config.config_manager import config

def create_kafka_consumer(topic, group_id="default_group"):
    """Creates and returns a Kafka Consumer configured for a specific topic and group."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=[config.kafka_server],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def create_kafka_producer():
    """Creates and returns a Kafka Producer."""
    return KafkaProducer(
        bootstrap_servers=[config.kafka_server],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

def send_message(producer, topic, message):
    """Sends a message to a specified topic using the given producer."""
    producer.send(topic, value=message)
    producer.flush()  # Ensure all messages are sent before returning

def receive_messages(consumer, handle_message):
    """Receives messages from a specified consumer and processes them using a callback function."""
    for message in consumer:
        handle_message(message)
