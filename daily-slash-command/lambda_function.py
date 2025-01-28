import json
import base64
import urllib

import boto3

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client('lambda', region_name='us-east-1')


def get_response_url(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    response_url = body_dict['response_url']
    return response_url
    
    
def get_slash_text(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    text = body_dict.get('text', '')
    return text


def get_command(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    command = body_dict['command']
    return command


def get_body_dict(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    return body_dict
    

def lambda_handler(event, context):
    response_url = get_response_url(event)
    slash_text = get_slash_text(event)
    command = get_command(event)

    body_dict = get_body_dict(event)
    logger.info(
        json.dumps({
            "eventName": "DailySlashCommand",
            "slashCommand": command,
            "slashText": slash_text,
            "userId": body_dict['user_id'],
            "userName": body_dict['user_name'],
            "channelId": body_dict['channel_id'],
            "channelName": body_dict['channel_name']
        })
    )

    if command == '/smoldaily':
        slash_text = 'smol'
    
    response = lambda_client.invoke(
        FunctionName='awakened-bot-daily-slash-command-background',
        InvocationType='Event',
        Payload=json.dumps({
            'slack_response_url': response_url,
            'slack_slash_text': slash_text
        })
    )
    
    return ''

