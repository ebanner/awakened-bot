import json
import time

from botocore.exceptions import ClientError

from slack_sdk import WebClient

import boto3

ecs_client = boto3.client('ecs')


SLACKBOT_TOKEN_NAME = 'AWAKENED_SLACK_BOT_TOKEN'
CHANNEL_ID = 'chopping-wood'

# SLACKBOT_TOKEN_NAME = 'EDWARDS_SLACKBOT_DEV_WORKSPACE_TOKEN'
# CHANNEL_ID = 'general'

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


def get_running_count():
    response = ecs_client.describe_services(
        cluster="test2",
        services=["test5"]
    )
    services = response['services']
    service = services[0]
    running_count = service['runningCount']
    return running_count


def get_call_name(event):
    call_name = event['call_name']
    return call_name


def replace_emojis(call_name):
    call_name_with_emojis = call_name.replace(':coffee:', '☕️')
    return call_name_with_emojis


def register_call_with_slack(call_name):
    call_name_with_emojis = replace_emojis(call_name)
    response = slack_client.calls_add(
        title=call_name_with_emojis,
        external_unique_id='foobar',
        join_url='https://discord.com/channels/767118316526764053/1172970508988461186',
        desktop_app_join_url='discord:///channels/767118316526764053/1172970508988461186',
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

    print(response.data)

    return response.data


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


def get_call_name(event):
    call_name = event['call_name']
    return call_name


def lambda_handler(event, context):
    print(event)

    call_name = get_call_name(event)
    
    if call_name == 'end':
        call_id = get('call_id')
        end_call(call_id)

    else:
        update_ecs_service(desired_count=1)
        while get_running_count() != 1:
            time.sleep(1)
            print('.')
        call_id = register_call_with_slack(call_name)

        print('call_id', call_id)

        post_call_to_channel(call_id)
        put('call_id', call_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

