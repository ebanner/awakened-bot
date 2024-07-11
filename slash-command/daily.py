import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Your bot user OAuth access token
SLACK_BOT_TOKEN = os.environ
# Channel ID where you want to send the message
CHANNEL_ID = 'general'

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

def lambda_handler(event, context):
    try:
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text="Hello, World!"
        )   
        assert response["ok"]
        print(f"Message sent successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
