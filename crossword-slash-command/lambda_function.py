import json
import base64
import boto3
import urllib.parse
import os
import re
from datetime import datetime, timedelta, timezone

from slack_sdk import WebClient

s3_client = boto3.client('s3')

sch = boto3.client("scheduler")


def put(key, value, bucket='storage9'):
    s3_client.put_object(Bucket=bucket, Key=key, Body=value)

def get(key, bucket='storage9'):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    value = object['Body'].read().decode('utf-8')
    return json.loads(value)


SLACK_WORKSPACE = 'awakened'
SLACK_BOT_TOKEN = os.environ['AWAKENED_SLACK_BOT_TOKEN']
CROSSWORDS_CHANNEL_NAME = 'crosswords'
CROSSWORDS_CHANNEL_ID = 'C091H60A9TN'
GAMES_CHANNEL_NAME = 'games'
GAMES_CHANNEL_ID = 'C4TC1CB3P'

# SLACK_WORKSPACE = "Edward's Slackbot Dev Workspace"
# SLACK_BOT_TOKEN = os.environ['EDWARDS_SLACKBOT_DEV_SLACK_BOT_TOKEN']
# CROSSWORDS_CHANNEL_NAME = 'general'
# CROSSWORDS_CHANNEL_ID = 'C04C5AVUMQF'
# GAMES_CHANNEL_NAME = 'general'
# GAMES_CHANNEL_ID = 'C04C5AVUMQF'

slack_client = WebClient(SLACK_BOT_TOKEN)


def send_message_thread(user, crossword_type):
    if crossword_type == 'crosswordclub':
        return
        
    def get_latest_crossword_thread_ts():
        response = None
        if crossword_type == "crosswordclub":
            response = slack_client.conversations_history(channel=GAMES_CHANNEL_ID, limit=10)
        else:
            response = slack_client.conversations_history(channel=CROSSWORDS_CHANNEL_ID, limit=10)
        for message in response["messages"]:
            if crossword_type in message["text"]:
                return message["ts"]

    latest_crossword_thread_ts = get_latest_crossword_thread_ts()
    if latest_crossword_thread_ts is None:
        return

    if crossword_type == "crosswordclub":
        response = slack_client.chat_postMessage(
            channel=GAMES_CHANNEL_NAME,
            text=f"{user} is playing :wapo2:",
            thread_ts=latest_crossword_thread_ts
        )
    else:
        response = slack_client.chat_postMessage(
            channel=CROSSWORDS_CHANNEL_NAME,
            text=f"{user} is playing :wapo2:",
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


def get_daily_games_message():
    response = slack_client.conversations_history(
        channel=GAMES_CHANNEL_ID,
        limit=10
    )
    
    for message in response['messages']:
        if 'The Dailies' in message['text']:
            return message


def handle_crossword_command(event, emoji=None):
    url = get_slash_text(event)
    crossword_type = get_crossword_type(event)

    latest_crossword_urls = get('wapo-url')
    latest_crossword_urls[crossword_type] = url
    put('wapo-url', json.dumps(latest_crossword_urls))

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
                            *(
                                [{
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/eddie/{crossword_type}",
                                        "text": "Eddie link"
                                    }
                                ]
                                }] if emoji != 'vox' else []
                            ),
                            *(
                                [{
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/katherine/{crossword_type}",
                                        "text": "Katherine link"
                                    }
                                ]
                                }] if emoji != 'lat' else []
                            ),
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "url": f"{lambda_url}/abhay/{crossword_type}",
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
    
    if crossword_type == 'crosswordclub':
        daily_games_message = get_daily_games_message()
        response = slack_client.chat_postMessage(
            channel=GAMES_CHANNEL_NAME,
            thread_ts=daily_games_message['ts'],
            blocks=message_blocks["blocks"],
            unfurl_links=False,
            unfurl_media=False
        )
    else:
        response = slack_client.chat_postMessage(
            channel=CROSSWORDS_CHANNEL_NAME,
            blocks=message_blocks["blocks"]
        )


def get_crossword_type(event):
    url = get_slash_text(event)
    match = re.search(r'https?://(?:www\.)?([^./]+)\.com', url)
    if match:
        crossword_type = match.group(1)
        return crossword_type
    else:
        return 'unknown'


def kick_off_eventbridge(crossword_url, crossword_type):
    SCHEDULE_NAME = "run-ecs-task-via-lambda"
    GROUP_NAME = "default"

    # Set schedule to run now for 15 minutes
    start = datetime.now(timezone.utc) + timedelta(seconds=5)
    end = start + timedelta(minutes=15)

    # Get the existing schedule
    existing = sch.get_schedule(Name=SCHEDULE_NAME, GroupName=GROUP_NAME)
    target = existing["Target"]

    # Inject the dynamic input payload for Lambda
    target["Input"] = json.dumps({
        "crossword_url": crossword_url,
        "crossword_type": crossword_type,
        "slack_workspace": SLACK_WORKSPACE,
    })

    # Update schedule
    sch.update_schedule(
        Name=SCHEDULE_NAME,
        GroupName=GROUP_NAME,
        ScheduleExpression="rate(1 minute)",
        StartDate=start,
        EndDate=end,
        FlexibleTimeWindow={"Mode": "OFF"},
        Target=target,
        State="ENABLED"
    )

    print(f"Updated {SCHEDULE_NAME} to run with crossword_url={crossword_url}")


def lambda_handler(event, context):
    user_agent = get_user_agent(event)
    if user_agent == 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)':
        return {
            "statusCode": 200
        }

    slash_command = get_slash_command(event)
    if slash_command == "/crossword-debug":
        latest_crossword_urls = get('wapo-url')
        return {
            "statusCode": 200,
            "body": f'`{json.dumps(latest_crossword_urls)}`'
        }

    elif slash_command == "/crossword":
        url = get_slash_text(event)

        emojis = { 
            'washingtonpost':'wapo',
            'vox': 'vox',
            'morningbrew': 'coffee',
            'newyorker': 'owl',
            'nymag': 'nymag',
            'theatlantic': 'theatlantic',
            'nypost': 'nypost',
            'crosswordclub': 'cc',
            'latimes': 'lat'
        }

        crossword_type = get_crossword_type(event)
        emoji = emojis.get(crossword_type)

        handle_crossword_command(event, emoji)
        return {
            "statusCode": 200
        }

    elif slash_command == "/smolcrossword":
        url = get_slash_text(event)

        emojis = { 
            'washingtonpost':'wapo',
            'vox': 'vox',
            'morningbrew': 'coffee',
            'newyorker': 'owl',
            'nymag': 'nymag',
            'theatlantic': 'theatlantic',
            'nypost': 'nypost',
            'crosswordclub': 'cc',
            'latimes': 'lat'
        }

        crossword_type = get_crossword_type(event)
        emoji = emojis.get(crossword_type)

        handle_crossword_command(event, emoji)

        return {
            "statusCode": 200
        }

    else:
        raw_path = event.get('rawPath')
        _, user, crossword_type = raw_path.split('/')

        if user == 'eddie':
            send_message_thread('Eddie', crossword_type)
        elif user == 'katherine':
            send_message_thread('Katherine', crossword_type)
        elif user == 'abhay':
            send_message_thread('Abhay', crossword_type)

        print("CHECKING CROSSWORD_TYPE", crossword_type)
        if crossword_type in ['crosswordclub']:
            print("KICKING OFF EVENTBRIDGE")
            latest_crossword_urls = get('wapo-url')
            crossword_url = latest_crossword_urls[crossword_type]
            kick_off_eventbridge(crossword_url, crossword_type)

        latest_crossword_urls = get('wapo-url')
        return {
            "statusCode": 302,
            "headers": {
                "Location": latest_crossword_urls[crossword_type]
            }
        }

