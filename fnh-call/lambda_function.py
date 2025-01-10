import json

import base64
import urllib.parse

import boto3

from botocore.exceptions import ClientError

from slack_sdk import WebClient


SLACKBOT_TOKEN_NAME = 'AWAKENED_SLACK_BOT_TOKEN' #'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN'

CHANNEL_ID = 'U02780B5563' #'general'

s3 = boto3.client('s3')

BUCKET = 'storage9'


def get_slack_token(slackbot_token_name):
    secret_name = slackbot_token_name
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']

    result = json.loads(secret)

    return result[secret_name]


slack_token = get_slack_token(SLACKBOT_TOKEN_NAME)
slack_client = WebClient(token=slack_token)


def put(key, value):
    s3.put_object(Bucket=BUCKET, Key=key, Body=value)


def get(key):
    """If there is no key entry then return None"""

    object = s3.get_object(Bucket=BUCKET, Key=key)

    value = object['Body'].read().decode('utf-8')
    return value


def register_call_with_slack():
    response = slack_client.calls_add(
        external_unique_id='foobar',
        join_url='https://discord.com/channels/767118316526764053/1172970508988461186',
        desktop_app_join_url='discord:///channels/767118316526764053/1172970508988461186',
        title='Friday Night Hangout',
    )

    call_id = response.data['call']['id']

    return call_id


def post_call_to_channel(call_id):
    blocks = [
        {
            'type': 'call',
            'call_id': call_id
        }
    ]

    response = slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        blocks=blocks,
    )

    return response.data


def add_participant_to_call(user):
    users = [
        user
    ]   

    call_id = get('call_id')
    response = slack_client.calls_participants_add(
        id=call_id,
        users=users
    )   

    return response.data


def remove_participant_from_call(user):
    users = [ 
        user
    ]   
    call_id = get('call_id')
    response = slack_client.calls_participants_remove(
        id=call_id,
        users=users
    )

    return response.data


def is_slash_command(event):
    def get_body_dict(event):
        body_base64_encoded = event['body']
        body_bytes = base64.b64decode(body_base64_encoded)
        body_decoded = body_bytes.decode('utf-8')
        body_dict = dict(urllib.parse.parse_qsl(body_decoded))
        return body_dict

    if 'isBase64Encoded' not in event or not event['isBase64Encoded']:
        return False

    body_dict = get_body_dict(event)
    return body_dict['command'] == '/fnh'


def is_participant_joined_event(event):
    body_json = event['body']
    body = json.loads(body_json)
    return body['event'] == 'participant_joined'


def is_participant_left_event(event):
    body_json = event['body']
    body = json.loads(body_json)
    return body['event'] == 'participant_left'


def get_user(event):
    if SLACKBOT_TOKEN_NAME == 'AWAKENED_SLACK_BOT_TOKEN':
        DISCORD_TO_SLACK_MAP = {
            'edward4346': 'U02780B5563'
        }
    else:
        assert SLACKBOT_TOKEN_NAME == 'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN'
        DISCORD_TO_SLACK_MAP = {
            'edward4346': 'U04CYG7MEKB'
        }

    body_json = event['body']
    body = json.loads(body_json)
    discord_user_name = body['user_name']

    if discord_user_name in DISCORD_TO_SLACK_MAP:
        user = { 
            "slack_id": DISCORD_TO_SLACK_MAP[discord_user_name]
        }
    else:
        user = {   
            "external_id": discord_user_name,
            "display_name": discord_user_name,
            # "avatar_url": "https://example.com/users/avatar1234.jpg"
        }

    return user


def end_call(call_id):
    slack_client.calls_end(
        id=call_id
    )

def get_slash_text(event, default='begin'):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    text = body_dict.get('text', default)
    return text


def lambda_handler(event, context):
    if is_slash_command(event):
        slash_text = get_slash_text(event)
        if slash_text == 'begin':
            call_id = register_call_with_slack()
            post_call_to_channel(call_id)
            put('call_id', call_id)
            return {
                'statusCode': 200,
                'body': ''
            }
        else:
            assert slash_text == 'end'
            call_id = get('call_id')
            end_call(call_id)
            return {
                'statusCode': 200,
                'body': ''
            }

    elif is_participant_joined_event(event):
        user = get_user(event)
        add_participant_to_call(user)
        return {
            'statusCode': 200,
            'body': 'ok'
        }

    elif is_participant_left_event(event):
        user = get_user(event)
        remove_participant_from_call(user)
        return {
            'statusCode': 200,
            'body': 'ok'
        }

