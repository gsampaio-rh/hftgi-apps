from flask import Flask, Response, render_template
from kafka import KafkaConsumer
import json
import argparse
import time
import html

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run Flask app in test or normal mode.")
parser.add_argument(
    "--test",
    action="store_true",
    help="Run the app in test mode using static JSON data.",
)

args = parser.parse_args()

app = Flask(__name__)

TOPIC_NAME="answer"

def create_consumer():
    """Function to create a new KafkaConsumer instance for each request."""
    return KafkaConsumer(
        "answer",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=None,  # Using None or a unique group_id for each consumer can help avoid conflicts
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        session_timeout_ms=6000,
        heartbeat_interval_ms=1000,
    )

def preprocess_summary(summary):
    """Preprocesses the summary text to make it more readable."""
    # Decode HTML entities and escape sequences
    summary = html.unescape(summary)
    # Strip leading and trailing whitespaces and normalize newlines
    summary = summary.strip().replace('\n', ' ').replace('\r', ' ')
    # Optional: further processing like removing excessive whitespace
    summary = ' '.join(summary.split())
    
    # Find the position of the first period and slice the summary up to that point
    # Also, ensure that we handle cases where there's no period in the summary
    period_index = summary.find('.')
    if period_index != -1:
        summary = summary[:period_index + 1]  # Include the period in the summary

    # Strip leading and trailing whitespaces
    summary = summary.strip()
    
    return summary

def chat_json_response(message_dict):
    """Prepares a JSON response for the frontend from the Kafka message."""
    # Extract top-level and nested data from the message_dict
    json_response = {
        "id": message_dict.get("conversation_id"),
        "conversation": message_dict.get("conversation_text"),
        "name": message_dict['data'].get("name"),
        "email": message_dict['data'].get("email"),
        "phone_number": message_dict['data'].get("phone_number"),
        "location": message_dict['data'].get("location"),
        "department": message_dict['data'].get("department"),
        "issue": message_dict['data'].get("issue"),
        "service": message_dict['data'].get("service"),
        "additional_information": message_dict['data'].get("additional_information"),
        "detailed_description": message_dict['data'].get("detailed_description"),
        "intent": message_dict.get("intent"),
        "sentiment": message_dict.get("sentiment"),
        "summary": preprocess_summary(message_dict.get("summary", "")),
        "output_score": message_dict.get("output_score")
    }

    return json_response

@app.route("/stream")
def stream():
    """Route to stream Kafka messages to clients using Server-Sent Events."""

    def generate_messages():
        # Check if we are in test mode based on command-line argument
        if args.test:
            # Path to your test.json file
            print("##### TEST MODE #####")
            test_json_path = 'test_data/test.json'
            with open(test_json_path, 'r') as file:
                data = json.load(file)
                json_response = chat_json_response(data)
                # Simulate a message stream by sleeping and yielding the test data
                while True:
                    yield f"data: {json.dumps(json_response)}\n\n"
                    time.sleep(10)  # Adjust time as needed
        else:
            consumer = create_consumer()  # Create a new consumer instance for this request
            for message in consumer:
                try:
                    message_dict = message.value
                    json_response = chat_json_response(message_dict)

                    # Sending only the json_response part to the client
                    yield f"data: {json.dumps(json_response)}\n\n"
                except json.JSONDecodeError:
                    # Handle case where message value is not a valid JSON string
                    print(f"Error decoding JSON for message: {message.value}")

    return Response(generate_messages(), mimetype="text/event-stream")

@app.route("/messages")
def messages():
    """Renders the initial HTML page."""
    return render_template("messages.html")

if __name__ == "__main__":
    app.run(debug=True)
