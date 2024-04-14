# config_manager.py

import os

class Config:
    """ Configuration manager class to hold all environment variables and defaults. """

    def __init__(self):
        """ Initialize the configuration settings. """
        self.inference_server_url = os.getenv(
            "INFERENCE_SERVER_URL", 
            "https://hf-tgi-server-llms.apps.cluster-45cdc.45cdc.openshift.opentlc.com"
        )
        self.kafka_server = os.getenv("KAFKA_SERVER", "localhost:9092")
        self.consumer_topic = os.getenv("CONSUMER_TOPIC", "chat")
        self.producer_topic = os.getenv("PRODUCER_TOPIC", "answer")
        self.csv_file_path = os.getenv("CSV_FILE_PATH", "conversation_results.csv")

    def __str__(self):
        """ String representation for easy debugging. """
        return (f"Inference Server URL: {self.inference_server_url}\n"
                f"Kafka Server: {self.kafka_server}\n"
                f"Consumer Topic: {self.consumer_topic}\n"
                f"Producer Topic: {self.producer_topic}\n"
                f"CSV File Path: {self.csv_file_path}")

# This allows the config instance to be available across the application.
config = Config()
