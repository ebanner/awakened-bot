import json

import base64
import urllib.parse

import boto3

from botocore.exceptions import ClientError

from slack_sdk import WebClient


SLACKBOT_TOKEN_NAME = 'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN'

CHANNEL_ID = 'general'

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
        join_url='https://discord.com/channels/974552137780584528/974553089765961758',
        desktop_app_join_url='discord:///channels/974552137780584528/974553089765961758',
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


def add_participant_to_call(user_name):
    users = [
        # { 
        #     "slack_id": "U04CYG7MEKB"
        # }, 
        {   
            "external_id": "54321678",
            "display_name": user_name,
            # "avatar_url": "https://example.com/users/avatar1234.jpg"
        }   
    ]   

    call_id = get('call_id')
    response = slack_client.calls_participants_add(
        id=call_id,
        users=users
    )   

    return response.data


def remove_participant_from_call(user_name):
    users = [ 
        # { 
        #     "slack_id": "U04CYG7MEKB"
        # }, 
        {   
            "external_id": "54321678",
            "display_name": user_name,
            # "avatar_url": "https://example.com/users/avatar1234.jpg"
        }   
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

    print(event)

    body_dict = get_body_dict(event)
    return body_dict['command'] == '/fnh'


def lambda_handler(event, context):
    if is_slash_command(event):
        print('slash command')
        call_id = register_call_with_slack()
        post_call_to_channel(call_id)
        put('call_id', call_id)
    elif is_participant_joined_event(event):
        print('participant joined')
        # user_name = get_user_name(event)
        # add_participant_to_call(user_name)
    elif is_participant_left_event(event):
        # user_name = get_user_name(event)
        print('participant left') 

    return {
        'statusCode': 200,
        'body': ''
    }
