import os

import discord

import requests

import json


from dotenv import load_dotenv
load_dotenv()


LAMBDA_URL = os.environ['LAMBDA_URL']


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
        response = emit_participant_joined_event(user_name)
        print(response)

    elif is_leave_event(before, after):
        user_name = member.name
        response = emit_participant_left_event(user_name)
        print(response)


if __name__ == '__main__':
    DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
    discord_client.run(DISCORD_BOT_TOKEN)
