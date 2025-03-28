import os
import json
import requests

import discord

import boto3


from dotenv import load_dotenv
load_dotenv()

import asyncio



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
    def get_awakened_guild(guilds):
        for guild in guilds:
            if guild.name == "Press A to Awaken":
                return guild

    def get_space_voice_channel(voice_channels):
        for voice_channel in voice_channels:
            if voice_channel.name == "Space":
                return voice_channel

    awakened_guild = get_awakened_guild(discord_client.guilds)
    space_voice_channel = get_space_voice_channel(awakened_guild.voice_channels)

    for member in space_voice_channel.members:
        emit_participant_joined_event(member.name)


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
            asyncio.create_task(wait_maybe_end_call(before.channel))


async def wait_maybe_end_call(channel):
    await asyncio.sleep(60)

    num_members = len(channel.members)
    if num_members == 0:
        emit_end_call_event()


if __name__ == '__main__':
    # DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
    discord_bot_token = get_secret('DISCORD_BOT_TOKEN', 'DISCORD_BOT_TOKEN')
    discord_client.run(discord_bot_token)

