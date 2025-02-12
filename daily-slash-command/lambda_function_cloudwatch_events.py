import json
import gzip
import base64
import boto3

import gspread


secrets_client = boto3.client("secretsmanager")


def get_secret(secret_name, secret_key=None):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    result = response['SecretString']
    secrets = json.loads(result)

    if secret_key:
        return secrets[secret_key]
    else:
        return secrets

creds = get_secret('AWAKENED_DAILY_SLASH_COMMAND_ETL')
credentials_json = creds['SERVICE_ACCOUNT_KEY_JSON']
credentials_dict = json.loads(credentials_json)

gsheets_client = gspread.service_account_from_dict(credentials_dict)


def is_daily_slash_command_event(log_event_data):
    for log_event in log_event_data['logEvents']:
        message = log_event['message']
        if 'DailySlashCommand' in message:
            return True
    return False


def extract_log_event_json(message):
    log_event_json = message.split('\t')[3]
    return log_event_json


def get_daily_slash_command_event(log_event_data):
    for log_event in log_event_data['logEvents']:
        message = log_event['message']
        if 'DailySlashCommand' not in message:
            continue

        log_event_json = extract_log_event_json(message)
        structured_log = json.loads(log_event_json)
        ts = log_event["timestamp"]
        structured_log["timestamp"] = ts
        return structured_log

def get_date_string(timestamp_ms):
    from datetime import datetime
    unix_timestamp = timestamp_ms / 1000
    dt = datetime.utcfromtimestamp(unix_timestamp)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time


def lambda_handler(event, context):
    logs_b64_encoded = event['awslogs']['data']
    compressed_data = base64.b64decode(logs_b64_encoded)
    decompressed_data = gzip.decompress(compressed_data)
    log_event_data = json.loads(decompressed_data)

    if not is_daily_slash_command_event(log_event_data):
        return {
            'statusCode': 200,
            'body': json.dumps('No daily slash command event')
        }

    print(log_event_data)

    daily_slash_command_event = get_daily_slash_command_event(log_event_data)

    print('DailySlashCommandEvent', daily_slash_command_event)

    event = daily_slash_command_event
    fullCommand = event['slashCommand'] + (' ' + event['slashText'] if event['slashText'] else '')
    dateString = get_date_string(event['timestamp'])
    
    row = dateString, event['slashCommand'], event['slashText'], event['userId'], event['userName'], event['channelId'], event['channelName'], fullCommand

    spreadsheet = gsheets_client.open('Awakened Daily Slash Command')
    worksheet = spreadsheet.worksheet('Sheet1')

    result = worksheet.append_row(row)
    print(result)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

