import json
import base64
import boto3
import urllib.parse
import os

from slack_sdk import WebClient

s3_client = boto3.client('s3')

def put(key, value, bucket='storage9'):
    s3_client.put_object(Bucket=bucket, Key=key, Body=value)

def get(key, bucket='storage9'):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    value = object['Body'].read().decode('utf-8')
    return value

# SLACK_BOT_TOKEN = os.environ['EDWARDS_SLACKBOT_DEV_SCK_BOT_TOKEN']
SLACK_BOT_TOKEN = os.environ['AWAKENED_SLACK_BOT_TOKEN']
slack_client = WebClient(SLACK_BOT_TOKEN)

def send_message(user):
    response = slack_client.chat_postMessage(
        channel='crossword-alerts',
        text=f"{user} is playing the crossword!"
    )

def get_slash_text(event):
    if 'body' not in event:
        return None
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    text = body_dict.get('text', '')
    return text


def lambda_handler(event, context):
    url = get_slash_text(event)
    if url:
        put('wapo-url', url)
        lambda_url = os.environ["LAMBDA_URL"]
        message_blocks = {
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"<{url}|Collab crossword>"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"• <{lambda_url}/eddie|Eddie link>\n• <{lambda_url}/katherine|Katherine link>\n• <{lambda_url}/abhay|Abhay link>"}}
            ]
        }
        return {
            "statusCode": 200,
            "body": json.dumps(message_blocks),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    if event.get('rawPath') == '/eddie':
        send_message('Eddie')
    elif event.get('rawPath') == '/katherine':
        send_message('Katherine')
    elif event.get('rawPath') == '/abhay':
        send_message('Abhay')

    url = get('wapo-url')
    return {
        "statusCode": 302,
        "headers": {
            "Location": url
        }
    }

