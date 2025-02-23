import os
import json
import requests

import discord

import boto3


from dotenv import load_dotenv
load_dotenv()


LAMBDA_URL = os.environ['LAMBDA_URL']
secrets_client = boto3.client("secretsmanager")

def get_secret(secret_name, secret_key=None):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    result = response['SecretString']
    secrets = json.loads(result)

    if secret_key:
        return secrets[secret_key]
    else:
        return secrets


def emit_participant_joined_event(user_name):
    response = requests.post(
        LAMBDA_URL,
        data=json.dumps({
            'event': 'participant_joined',
            'user_name': user_name
        }),
        headers={
            'Content-Type': 'application/json'
        }
    )
    print(response.text)
    return response.text


def emit_participant_left_event(user_name):
    response = requests.post(
        LAMBDA_URL,
        data=json.dumps({
            'event': 'participant_left',
            'user_name': user_name
        }),
        headers={
            'Content-Type': 'application/json'
        }
    )
    print(response.text)
    return response.text


def emit_end_call_event():
    response = requests.post(
        LAMBDA_URL,
        data=json.dumps({
            'event': 'end_call',
        }),
        headers={
            'Content-Type': 'application/json'
        }
    )
    print(response.text)
    return response.text


intents = discord.Intents.default()
intents.all()
discord_client = discord.Client(intents=intents)


@discord_client.event
async def on_ready():
    print('Ready!')


@discord_client.event
async def on_voice_state_update(member, before, after):
    def is_join_event(before, after):
        return not before.channel and after.channel

    def is_leave_event(before, after):
        return before.channel and not after.channel

    if is_join_event(before, after):
        user_name = member.name
        emit_participant_joined_event(user_name)

    elif is_leave_event(before, after):
        user_name = member.name
        emit_participant_left_event(user_name)

        num_members = len(before.channel.members)
        if num_members == 0:
            emit_end_call_event()


if __name__ == '__main__':
    # DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
    discord_bot_token = get_secret('DISCORD_BOT_TOKEN', 'DISCORD_BOT_TOKEN')
    discord_client.run(discord_bot_token)

