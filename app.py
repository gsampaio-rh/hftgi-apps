# app.py

from os import listdir
from os.path import isfile, join
import argparse
import logging
from config.config_manager import config
from config.vector_db_setup import initialize
from services.kafka_service import create_kafka_consumer, create_kafka_producer, send_message, receive_messages
from llms.llm_config import llm_config
from utilities.helpers import pretty_print_json, process_text_and_extract_data

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the AI model in local or Kafka mode.")
    parser.add_argument("--local-mode", action="store_true", help="Run the application in local mode without Kafka.")
    parser.add_argument("--vector-memory", action="store_true", help="Run the application with a FAISS vector store")
    parser.add_argument("--directory-path", type=str, default="data/conversations", help="Directory path for local mode data processing.")
    return parser.parse_args()

def handle_message(message):
    """Process messages received from Kafka."""
    response = llm_config.invoke(message.value['conversation'])
    # pretty_print_json(response)  # For demonstration, print the processed result
    # send_message(producer, config.producer_topic, response)

def run_kafka_mode():
    """Set up and process data using Kafka consumers and producers."""
    consumer = create_kafka_consumer(config.consumer_topic, "chat-group")
    producer = create_kafka_producer()

    receive_messages(consumer, handle_message)

def run_local_mode(directory_path):
    """Process all text files in the given directory as conversations."""
    
    files = [join(directory_path, f) for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith('.txt')]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                conversation_text = file.read().strip()
            if conversation_text:
                logging.debug(f"Processing file: {file_path}")
                llm_processed_output = process_text_and_extract_data(conversation_text)
                logging.info(f"Processed Output for {file_path}: {llm_processed_output}")
        except Exception as e:
            logging.error(f"Failed to process file {file_path}: {e}")


def main():
    args = parse_args()
    
    # Initialize the vector database with content from markdown files
    if args.vector_memory:
        index, file_paths = initialize(content_directory='./content')

    if args.local_mode:
        logging.info("Running in local mode.")
        run_local_mode(args.directory_path)
    else:
        logging.info("Running in Kafka mode.")
        run_kafka_mode()

if __name__ == "__main__":
    main()
