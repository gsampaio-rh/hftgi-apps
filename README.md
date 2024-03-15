# Hugging Face Text Inference Apps

**Hugging Face Text Inference Apps** demonstrates the integration of Hugging Face's Large Language Models (LLMs) with Kafka for real-time text processing and inference. This small-scale project showcases how to leverage cutting-edge NLP technologies to analyze, understand, and interact with text data streamed through Kafka messaging systems.

## Components

- **[LangChain](https://github.com/hwchase17/langchain)**: Provides the backbone for generating responses and analyzing texts using Large Language Models.
- **Kafka Integration**: Utilizes KafkaConsumer and KafkaProducer for consuming and producing messages within a Kafka cluster.
- **[HuggingFace LLMs](https://huggingface.co/models)**: Leverages HuggingFace's APIs for text generation and embeddings to enhance response quality and contextual understanding.

## Features

- **Conversation Handling**: Processes incoming chat messages from a Kafka topic, extracting structured information and analyzing sentiment.
- **Information Extraction**: Converts chat messages into structured JSON format, identifying key pieces of information such as names, emails, and issues described within the conversation.
- **Sentiment Analysis**: Analyzes the sentiment of the conversations, categorizing them as positive or negative based on the content.
- **Kafka Communication**: Consumes messages from a designated chat topic and publishes responses to an answer topic, facilitating real-time chat interaction.

## Prerequisites

- Python 3.x
- Kafka cluster setup
- Access to HuggingFace API for embeddings and text generation
- Necessary Python libraries: `langchain`, `kafka-python`, `json`, `logging`, `uuid`

## How the application works

To convert the example conversation into a structured JSON format as shown, the application performs several steps. Below is a brief explanation of each step involved in the process:

1. **Receive Conversation**: The application listens for messages on the Kafka `chat` topic, each message containing a conversation similar to the provided example.

2. **Extract Information**: Upon receiving a message, the application utilizes predefined templates and Natural Language Processing (NLP) techniques to extract key pieces of information from the conversation. This includes names, emails, phone numbers, departments, issues, and any additional relevant details.

3. **Perform Sentiment Analysis**: In addition to extracting structured information, the application performs sentiment analysis on parts of the conversation (like the detailed description of the issue) to determine the overall sentiment as "Positive" or "Negative". This is achieved using sentiment analysis models available through Hugging Face's APIs.

4. **Generate Structured JSON**: The extracted information and sentiment analysis result are then compiled into a structured JSON format. This JSON object includes fields such as `name`, `email`, `phone_number`, `department`, `issue`, `service`, `additional_information`, and a nested object for `sentiment_analysis`.

5. **Publish Results**: Finally, the structured JSON is packaged with a unique `id` and the original `conversation` text, and then published to the Kafka `answer` topic. This allows downstream applications or services to consume and act upon the processed data.

This process showcases the powerful combination of NLP for text analysis and Kafka for real-time messaging, enabling the automated handling and analysis of conversational data.

### Conversation Input

```txt
Entrevistador: Olá, como posso ajudá-lo hoje? Vamos começar com algumas perguntas básicas. Qual é o seu nome?
Pessoa: Meu nome é Maria Costa.

Entrevistador: Ótimo, Maria Costa! Qual é o seu email?
Pessoa: Meu email é maria.costa@email.com.

Entrevistador: Perfeito! E qual é o número do seu telefone celular?
Pessoa: Meu número de telefone celular é (31) 77777-6666.

Entrevistador: Agora, precisamos de algumas informações específicas sobre a manifestação. Qual é o órgão relacionado com a manifestação?
Pessoa: O órgão relacionado é Departamento de Saúde.

Entrevistador: Entendido. E qual é o local relacionado à sua manifestação?
Pessoa: O local é Rua XV de Novembro, número 300, São Paulo.

Entrevistador: Certo. Qual é o serviço para o qual deve ser lançada a manifestação?
Pessoa: O serviço é atendimento de saúde.

Entrevistador: Ótimo. Sobre o que você gostaria de falar?
Pessoa: Eu gostaria de falar sobre falta de médicos nos postos de saúde da região central.

Entrevistador: Entendi. Quem são os envolvidos na sua manifestação?
Pessoa: Os envolvidos são pacientes que dependem do atendimento diário.

Entrevistador: Por último, pode descrever mais detalhes sobre sua manifestação?
Pessoa: Claro, a manifestação é sobre carência de profissionais de saúde que afeta o atendimento aos cidadãos locais.

Entrevistador: Muito obrigado pelas informações, Maria Costa! Vamos processar sua manifestação e entrar em contato em breve.
```

### JSON Output

```json
{
    "id": "78bd0fea-5c5f-4a7c-97ca-9be3803fe21d",
    "conversation": "Entrevistador: Olá, como posso ajudá-lo hoje? Vamos começar com algumas perguntas básicas. Qual é o seu nome?\nPessoa: Meu nome é Maria Costa.\n\nEntrevistador: Ótimo, Maria Costa! Qual é o seu email?\nPessoa: Meu email é maria.costa@email.com.\n\nEntrevistador: Perfeito! E qual é o número do seu telefone celular?\nPessoa: Meu número de telefone celular é (41) 66666-5555.\n\nEntrevistador: Agora, precisamos de algumas informações específicas sobre a manifestação. Qual é o órgão relacionado com a manifestação?\nPessoa: O órgão relacionado é Departamento de Trânsito.\n\nEntrevistador: Entendido. E qual é o local relacionado à sua manifestação?\nPessoa: O local é Rua XV de Novembro, número 300, São Paulo.\n\nEntrevistador: Certo. Qual é o serviço para o qual deve ser lançada a manifestação?\nPessoa: O serviço é manutenção de semáforos.\n\nEntrevistador: Ótimo. Sobre o que você gostaria de falar?\nPessoa: Eu gostaria de falar sobre demora na manutenção dos semáforos que está causando muitos congestionamentos.\n\nEntrevistador: Entendi. Quem são os envolvidos na sua manifestação?\nPessoa: Os envolvidos são moradores da região e os motoristas.\n\nEntrevistador: Por último, pode descrever mais detalhes sobre sua manifestação?\nPessoa: Claro, a manifestação é sobre urgência na manutenção dos semáforos na Avenida Paulista, causada por congestionamentos e acidentes.\n\nEntrevistador: Muito obrigado pelas informações, Maria Costa! Vamos processar sua manifestação e entrar em contato em breve.\n\n",
    "json_response": {
        "name": "Maria Costa",
        "email": "maria.costa@email.com",
        "phone_number": "(41) 66666-5555",
        "department": "Departamento de Trânsito",
        "issue": "Manifestação sobre urgência na manutenção de semáforos na Avenida Paulista",
        "service": "Manutenção de semáforos",
        "additional_information": "Manutenção de semáforos na Avenida Paulista, causada por congestionamentos e acidentes, com a urgência de manutenção.",
        "sentiment_analysis": {
            "text": "\nThe sentiment of the text is \"Positive\". The text discusses a public event and the importance of maintaining the infrastructure of the event. The text also mentions the importance of ensuring the safety of attendees and the need for efficient communication."
        }
    }
}
```

## Setup and Configuration

- Kafka server and topic configuration are required for message consumption and production.
- The HuggingFace inference server URL must be set for LLM operations.
- Logging is configured for monitoring and debugging purposes.

## Environment Setup 🌍

To set up your environment to run the code, first install all requirements:

1. 📥 Clone the repo using git:

```shell
git clone https://github.com/gsampaio-rh/hftgi-apps
```

2. Create and Activate a Virtual Environment:

```bash
  python -m venv .env
  source .env/bin/activate
```

3. 🛠️ Install the dependencies using pip

```shell
pip install -r requirements.txt
```

### Inference Server Setup

The inference server is responsible for performing text inference tasks using Hugging Face's Large Language Models. You need to specify the URL of the inference server that the application will communicate with.

- `inference_server_url` should be set to the URL of your Hugging Face inference server. If you're running the server locally for testing, you can use "http://localhost:3000/". For production or cloud environments, you would replace this with the actual URL of your deployed inference server.

### Kafka Setup

This application uses Kafka for message queueing, consuming messages from a chat topic, processing them, and then producing responses to an answer topic.

- `kafka_server` specifies the address of your Kafka server. If running locally, it's typically set to "localhost:9092". For production, this would be the address of your Kafka cluster.
- `consumer_topic` is the name of the Kafka topic from which the application will consume messages. This should be set to "chat" or whichever topic you have designated for incoming chat messages.
- `producer_topic` is the name of the Kafka topic to which the application will produce processed messages. This is set to "answer", or any other topic name where you want the processed messages to be published.

Ensure these settings are correctly configured to match your environment before running the application.

## Running the Application 🚀

To run the application, follow these steps:

1. **Run the Application**:

```bash
python app.py
```

## Contribution

Contributions to the `hftgi-apps` project are welcome. Whether you're fixing a bug, proposing a new feature, or improving the documentation, your support helps improve the project for everyone.

## License

The `hftgi-apps` project is open-sourced under a specified license, allowing for modification, personal use, and distribution within the terms of that license. Please review the license details for more information on your rights and restrictions.