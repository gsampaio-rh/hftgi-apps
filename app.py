# app.py

import argparse
import logging
import json
from os import listdir
from os.path import isfile, join
from config.config_manager import config
from services.vector_service import VectorDatabaseManager
from services.kafka_service import create_kafka_consumer, create_kafka_producer, send_message, receive_messages
from llms.llm_config import llm_config
from services.llm_processing import LLMProcessor
from services.document_management import DocumentManager
from utilities.helpers import top_words, pretty_print_json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Instantiate the manager
vector_db_manager = VectorDatabaseManager(content_directory='content', model_name='sentence-transformers/all-mpnet-base-v2')

# Create a DocumentManager instance using the existing vector_db_manager
doc_manager = DocumentManager(vector_db_manager)

# Create an instance of the LLMProcessor
processor = LLMProcessor()

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

def process_conversation(conversation_text, use_vector_memory=False):
    if conversation_text:
        llm_processed_output = processor.process_text_and_extract_data(conversation_text)

        result = json.loads(llm_processed_output)
        if result.get("intent") == "Information Request":
            logging.info("Information Request found")
            top = top_words(llm_processed_output)
            logging.info(f"Top words Output for {top}")

            # Retrieve documents based on the first keyword (most frequent)
            if top and use_vector_memory :  # Ensure there is at least one keyword
                documents = doc_manager.retrieve_documents(top[0][0])

                # Check if documents DataFrame is not empty
                if not documents.empty:
                    logging.info(f"Documents retrieved: {documents}")
                    # Convert DataFrame to JSON
                    documents_json = documents.to_json(orient='records')

                    # Save JSON string in the result dictionary
                    result["related_documents"] = json.loads(documents_json)
                else:
                    logging.info("No relevant documents were found for the top keyword.")
            else:
                logging.info("No keywords were extracted, thus no documents can be retrieved.")
        return result

def run_kafka_mode():
    """Set up and process data using Kafka consumers and producers."""
    consumer = create_kafka_consumer(config.consumer_topic, "chat-group")
    producer = create_kafka_producer()

    receive_messages(consumer, handle_message)

def run_local_mode(directory_path, use_vector_memory=False):
    """Process all text files in the given directory as conversations."""
    
    files = [join(directory_path, f) for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith('.txt')]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                conversation_text = file.read().strip()
                logging.info(f"Processing file: {file_path}")
                result = process_conversation(conversation_text, use_vector_memory)
                logging.info(f"Processed Output for {file_path}: {pretty_print_json(result)}")

        except Exception as e:
            logging.error(f"Failed to process file {file_path}: {e}")

def main():
    args = parse_args()

    # Initialize the vector database with content from markdown files
    if args.vector_memory:
        index, file_paths = vector_db_manager.initialize()
        # doc_manager.retrieve_documents("kafka")
    
    if args.local_mode:
        logging.info("Running in local mode.")
        run_local_mode(args.directory_path, args.vector_memory)
    else:
        logging.info("Running in Kafka mode.")
        run_kafka_mode()

if __name__ == "__main__":
    main()
