# Hugging Face Text Inference Apps

**Hugging Face Text Inference Apps** demonstrates the integration of Hugging Face's Large Language Models (LLMs) with Kafka for real-time text processing and inference. This small-scale project showcases how to leverage cutting-edge NLP technologies to analyze, understand, and interact with text data streamed through Kafka messaging systems.

## Components

- **Langchain LLMs**: Provides the backbone for generating responses and analyzing texts using Large Language Models.
- **Kafka Integration**: Utilizes KafkaConsumer and KafkaProducer for consuming and producing messages within a Kafka cluster.
- **HuggingFace Text Generation & Embeddings**: Leverages HuggingFace's APIs for text generation and embeddings to enhance response quality and contextual understanding.

## Features

- **Conversation Handling**: Processes incoming chat messages from a Kafka topic, extracting structured information and analyzing sentiment.
- **Information Extraction**: Converts chat messages into structured JSON format, identifying key pieces of information such as names, emails, and issues described within the conversation.
- **Sentiment Analysis**: Analyzes the sentiment of the conversations, categorizing them as positive or negative based on the content.
- **Kafka Communication**: Consumes messages from a designated chat topic and publishes responses to an answer topic, facilitating real-time chat interaction.

## Setup and Configuration

- Kafka server and topic configuration are required for message consumption and production.
- The HuggingFace inference server URL must be set for LLM operations.
- Logging is configured for monitoring and debugging purposes.

## Prerequisites

- Python 3.x
- Kafka cluster setup
- Access to HuggingFace API for embeddings and text generation
- Necessary Python libraries: `langchain`, `kafka-python`, `json`, `logging`, `uuid`

## Contribution

Contributions to the `hftgi-apps` project are welcome. Whether you're fixing a bug, proposing a new feature, or improving the documentation, your support helps improve the project for everyone.

## License

The `hftgi-apps` project is open-sourced under a specified license, allowing for modification, personal use, and distribution within the terms of that license. Please review the license details for more information on your rights and restrictions.