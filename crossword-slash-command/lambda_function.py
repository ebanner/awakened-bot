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

# SLACK_BOT_TOKEN = os.environ['EDWARDS_SLACKBOT_DEV_SLACK_BOT_TOKEN']
# GAMES_CHANNEL_NAME = 'general'
# GAMES_CHANNEL_ID = 'C04C5AVUMQF'

SLACK_BOT_TOKEN = os.environ['AWAKENED_SLACK_BOT_TOKEN']
GAMES_CHANNEL_NAME = 'games'
GAMES_CHANNEL_ID = 'C4TC1CB3P'

slack_client = WebClient(SLACK_BOT_TOKEN)

NOTIFICATIONS_CHANNEL_NAME = 'crossword-alerts'

def send_message(user):
    response = slack_client.chat_postMessage(
        channel=NOTIFICATIONS_CHANNEL_NAME,
        text=f"{user} is playing :wapo:"
    )

def send_message_thread(user):
    def get_latest_crossword_thread_ts():
        response = slack_client.conversations_history(channel=GAMES_CHANNEL_ID, limit=10)
        for message in response["messages"]:
            if "Collab crossword" in message["text"]:
                return message["ts"]

    latest_crossword_thread_ts = get_latest_crossword_thread_ts()
    if latest_crossword_thread_ts is None:
        return

    response = slack_client.chat_postMessage(
        channel=GAMES_CHANNEL_NAME,
        text=f"{user} is playing :wapo:",
        thread_ts=latest_crossword_thread_ts
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

def get_body_dict(event):
    if 'body' not in event:
        return None
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    return body_dict


def get_slash_command(event):
    if 'body' not in event:
        return None
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    slash_command = body_dict.get("command")
    return slash_command


def get_user_agent(event):
    headers = event.get('headers')
    if headers:
        return headers.get('user-agent')
    return None


def handle_crossword_command(event, emoji=None):
    url = get_slash_text(event)

    put('wapo-url', url)
    lambda_url = os.environ["LAMBDA_URL"]

    title_block = [
        {
            "type": "link",
            "url": url,
            "text": "Collab crossword"
        }
    ]
    if emoji:
        title_block.extend([
            {
                "type": "text",
                "text": " "
            },
            {
                "type": "emoji",
                "name": emoji
            }
        ])

    message_blocks = {
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "block1",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": title_block
                    },
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": " "
                            }
                        ]
                    },
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/eddie",
                                        "text": "Eddie link"
                                    }
                                ]
                            },
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/katherine",
                                        "text": "Katherine link"
                                    }
                                ]
                            },
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/abhay",
                                        "text": "Abhay link"
                                    }
                                ]
                            }
                        ]
                    },
                ],
            }
        ]
    }

    if not emoji:
        response = slack_client.chat_postMessage(
            channel=GAMES_CHANNEL_NAME,
            blocks=message_blocks["blocks"]
        )
    else:
        response = slack_client.chat_postMessage(
            channel=GAMES_CHANNEL_NAME,
            blocks=message_blocks["blocks"],
            unfurl_links=False,
            unfurl_media=False
        )


def lambda_handler(event, context):
    user_agent = get_user_agent(event)
    if user_agent == 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)':
        return {
            "statusCode": 200
        }

    slash_command = get_slash_command(event)
    if slash_command == "/crossword":
        handle_crossword_command(event)
        return {
            "statusCode": 200
        }

    elif slash_command == "/smolcrossword":
        url = get_slash_text(event)

        emoji = None
        if 'washingtonpost' in url:
            emoji = 'wapo'
        elif 'vox' in url:
            emoji = 'vox'
        elif 'morningbrew' in url:
            emoji = 'coffee'
        elif 'newyorker' in url:
            emoji = 'owl'
        elif 'nymag' in url:
            emoji = 'nymag'
        elif 'theatlantic' in url:
            emoji = 'theatlantic'
        elif 'nypost' in url:
            emoji = 'nypost'

        handle_crossword_command(event, emoji)
        return {
            "statusCode": 200
        }

    else:
        if event.get('rawPath') == '/eddie':
            send_message_thread('Eddie')
        elif event.get('rawPath') == '/katherine':
            send_message_thread('Katherine')
        elif event.get('rawPath') == '/abhay':
            send_message_thread('Abhay')

        url = get('wapo-url')
        return {
            "statusCode": 302,
            "headers": {
                "Location": url
            }
        }
