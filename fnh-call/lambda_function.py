import json

import base64
import urllib.parse

import boto3

from botocore.exceptions import ClientError

from slack_sdk import WebClient

lambda_client = boto3.client('lambda', region_name='us-east-1')

SLACKBOT_TOKEN_NAME = 'AWAKENED_SLACK_BOT_TOKEN'
CHANNEL_ID = 'chopping-wood'
ecs_client = boto3.client('ecs')
# CHANNEL_ID = 'U02780B5563'

# SLACKBOT_TOKEN_NAME = 'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN'
# CHANNEL_ID = 'general'

s3 = boto3.client('s3')

BUCKET = 'storage9'

if SLACKBOT_TOKEN_NAME == 'AWAKENED_SLACK_BOT_TOKEN':
    DISCORD_TO_SLACK_MAP = {
        'edward4346': 'U02780B5563',
        'katherine5510': 'UEH585CJE',
        '.ruitorres': 'U778VCCTS',
        'scoliosisyphus': 'U1CK5QKPT',
        'abhayance': 'U0XTHU2LR',
        'grant_sachs': 'U01EKNT75EZ',
        'aximilli': 'U012JP811UJ',
        'haveanicedavid': 'U246YJFFA',
        # 'srguile': 'U778VCCTS',
    }
elif SLACKBOT_TOKEN_NAME == 'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN':
    DISCORD_TO_SLACK_MAP = {
        'edward4346': 'U04CYG7MEKB'
    }
else:
    raise Error('Invalid slackbot token name')


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


def add_participant_to_call(user):
    users = [
        user
    ]   

    call_id = get('call_id')

    print('call_id', call_id)

    response = slack_client.calls_participants_add(
        id=call_id,
        users=users
    )   

    print(response.data)

    return response.data


def remove_participant_from_call(user):
    users = [ 
        user
    ]   

    call_id = get('call_id')

    print('call_id', call_id)

    response = slack_client.calls_participants_remove(
        id=call_id,
        users=users
    )

    print(response.data)

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
    return body_dict['command'].startswith('/')


def is_participant_joined_event(event):
    if 'body' not in event:
        return False
    body_json = event['body']
    body = json.loads(body_json)
    return body['event'] == 'participant_joined'


def is_end_call_event(event):
    if 'body' not in event:
        return False
    body_json = event['body']
    body = json.loads(body_json)
    return body['event'] == 'end_call'


def is_participant_left_event(event):
    if 'body' not in event:
        return False
    body_json = event['body']
    body = json.loads(body_json)
    return body['event'] == 'participant_left'


def get_user(event):
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

    print(user)

    return user
    

def get_slash_text(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    text = body_dict.get('text', '')
    return text


def kick_off_background_lambda(call_name):
    response = lambda_client.invoke(
        FunctionName='friday-night-hangout-background',
        InvocationType='Event',
        Payload=json.dumps({
            'call_name': call_name,
        })
    )

    print(response)


def update_ecs_service(desired_count):
    response = ecs_client.update_service(
        cluster="test2",
        service="test5",
        desiredCount=desired_count
    )

    print(response)


def end_call(call_id):
    update_ecs_service(desired_count=0)

    response = slack_client.calls_end(
        id=call_id
    )

    print(response)


def lambda_handler(event, context):
    def get_body_dict(event):
        body_base64_encoded = event['body']
        body_bytes = base64.b64decode(body_base64_encoded)
        body_decoded = body_bytes.decode('utf-8')
        body_dict = dict(urllib.parse.parse_qsl(body_decoded))
        return body_dict

    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        body_dict = get_body_dict(event)
        print(body_dict)
    else:
        print(event)
    
    if is_slash_command(event):
        slash_text = get_slash_text(event)
        if slash_text == '':
            return {
                'statusCode': 200,
                'body': 'You need to specify an event name `/event [name|end]`'
            }
        elif slash_text != 'end':
            call_name = slash_text
            kick_off_background_lambda(call_name)
            return {
                'statusCode': 200,
                'body': f'Starting {call_name} call (will take about 30 seconds)...'
            }
        else:
            assert slash_text == 'end'
            call_name = slash_text
            kick_off_background_lambda(call_name)
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

    elif is_end_call_event(event):
        call_id = get('call_id')
        end_call(call_id)


