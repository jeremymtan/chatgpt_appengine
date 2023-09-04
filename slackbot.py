import os
from google.cloud import firestore
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler


app = Flask(__name__)

# Initialize the Slack Bolt app with your Slack app's credentials
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
slack_handler = SlackRequestHandler(slack_app)


# Initialize Firestore client
db = firestore.Client()


# Function to insert a greeting into Firestore
def insert_greeting(user_id, greeting_text):
    greetings_ref = db.collection("greetings")
    greeting_doc = greetings_ref.document(user_id)
    greeting_doc.set({"greeting_text": greeting_text})


# Function to retrieve a greeting from Firestore
def get_greeting(user_id):
    greetings_ref = db.collection("greetings")
    greeting_doc = greetings_ref.document(user_id)
    greeting_data = greeting_doc.get()
    return greeting_data.get("greeting_text") if greeting_data else None


# Define a route for your Flask web app
@app.route("/")
def hello():
    return "Hello, this is your combined Flask and Slack Bolt app!"


# Define a route for your Slack Bolt events
@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Retrieve and process incoming Slack events using the Slack Bolt app
    request_data = request.get_json()

    # Print request_data and req for debugging
    print("Received request_data:", request_data)

    response = slack_handler.handle(request)

    return "", 200


# Define a message listener that handles greetings
@slack_app.message("Hello")
def respond_to_hello(message, say):
    user = message["user"]
    existing_greeting = get_greeting(user)

    if existing_greeting:
        say(f"Welcome back! Your previous greeting was: {existing_greeting}")
    else:
        say("Hello! This is your first greeting.")
        insert_greeting(user, "Hello with Flask")


if __name__ == "__main__":
    # Start your Slackbot on the specified port (3000 in this example)
    app.run()
