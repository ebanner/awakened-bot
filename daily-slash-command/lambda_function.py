import asyncio
import json
import os
import random
import re
import sqlite3
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
import requests
from slack_sdk import WebClient

from emojis import EMOJIS

session = aiohttp.ClientSession()

SLACK_BOT_TOKEN = os.environ['AWAKENED_SLACK_BOT_TOKEN']
GAMES_CHANNEL_NAME = 'games'
GAMES_CHANNEL_ID = 'C4TC1CB3P'

# SLACK_BOT_TOKEN = os.environ['EDWARDS_SLACKBOT_DEV_SLACK_BOT_TOKEN']
# GAMES_CHANNEL_NAME = 'general'
# GAMES_CHANNEL_ID = 'C04C5AVUMQF'

slack_client = WebClient(SLACK_BOT_TOKEN)


async def get_wordle_lotd():
    LOTD_URL = 'https://rkigvsdewg.execute-api.us-east-1.amazonaws.com/default/ygyl-python3-9/wordle-lotd'
    async with session.get(LOTD_URL) as response:
        wordle_lotd = await response.text()
    return wordle_lotd


async def get_wiby_url():    
    WIBY_URL = 'https://wiby.me/surprise'
    async with session.get(WIBY_URL) as response:
        wiby_text = await response.text()
    
    pattern = r"URL='(.*?)'"
    match = re.search(pattern, wiby_text)
    wiby_url = match.group(1)
    return wiby_url


async def get_random_word():
    wordnik_api_key = os.environ['WORDNIK_API_KEY']
    WORDNIK_URL = f'https://api.wordnik.com/v4/words.json/randomWord?minLength=5&maxLength=5&minCorpusCount=1&minDictionaryCount=1&api_key={wordnik_api_key}'
    async with session.get(WORDNIK_URL) as response:
        result = await response.json()
    random_word = result['word'].upper()
    return random_word


def get_today_song():
    def get_num_songs(cursor):
        cursor.execute("SELECT COUNT(*) FROM songs")
        num_songs, = cursor.fetchone()
        return num_songs
        
    def get_day_index():
        day_str = datetime.now().strftime("%Y%m%d")
        day_index = int(day_str)
        return day_index
        
    with sqlite3.connect("awakened_songs.db") as conn:
        cursor = conn.cursor()
        num_songs = get_num_songs(cursor)
        day_index = get_day_index()
        
        cursor.execute("SELECT * FROM songs WHERE [index] = ?", (day_index % num_songs,))
        index, title, url = cursor.fetchone()

        return index, title, url


def get_day():
    date_time_utc = datetime.now()
    date_time_est = date_time_utc - timedelta(hours=4)
    return date_time_est.month, date_time_est.day


async def get_today_event_str():
    month, day = get_day()
    api_url = 'https://api.api-ninjas.com/v1/historicalevents?month={}&day={}'.format(month, day)
    async with session.get(api_url, headers={'X-Api-Key': os.environ['API_NINJAS_KEY']}) as response:
        today_events = await response.json()
    today_event = random.choice(today_events)
    year = int(today_event['year'])

    suffix = None
    if year < 0:
        suffix = ' BC'
        year *= -1
    elif 0 <= year < 1000:
        suffix = ' AD'
    else:
        suffix = ''
    
    return f"On this day {year}{suffix}: {today_event['event']}"


def get_abhay_blocks():
    def get_date():
        date_time_utc = datetime.now()
        date_time_est = date_time_utc - timedelta(hours=4)
        formatted_date = date_time_est.strftime("%a %-m/%-d/%y")
        return formatted_date
        
    loop = asyncio.get_event_loop()
    today_event_str = loop.run_until_complete(get_today_event_str())
    
    random_wordle_emoji = random.choice(['wordle', 'wordle2'])
    random_connections_emoji = random.choice(['connections', 'connections2'])
    random_mini_emoji = random.choice(['mini', 'mini2', 'mini3'])

    date = get_date()
    abhay_blocks = [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "emoji",
                            "name": "wordle2",
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": "connections2"
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": "mini",
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": "plusword"
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "text",
                            "text": date,
                            "style": {
                                "bold": True
                            }
                        },
                    ]
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": today_event_str,
                }
            ]
        }
    ]
    return abhay_blocks


def get_emoji_name():
    emoji_name = random.choice(EMOJIS)
    return emoji_name


def get_eddie_blocks():
    def get_date():
        date_time_utc = datetime.now()
        date_time_est = date_time_utc - timedelta(hours=4)
        formatted_date = date_time_est.strftime("%A\n%B %d, %Y")
        return formatted_date
    
    date = get_date()
    loop = asyncio.get_event_loop()
    print('Making API calls')
    _, song_title, song_url = get_today_song()
    today_event_str, random_word, wordle_lotd, wiby_url = loop.run_until_complete(
        asyncio.gather(
            get_today_event_str(),
            get_random_word(),
            get_wordle_lotd(),
            get_wiby_url()
        )
    )
    print('wiby_url', wiby_url)
    print('Made API calls')
    emoji_name = get_emoji_name()
    
    random_mini_emoji = random.choice(['mini', 'mini2', 'mini3'])
    
    eddie_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "The Dailies"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "emoji",
                            "name": "wordle2",
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": "connections2",
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": random_mini_emoji,
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "emoji",
                            "name": "plusword"
                        },
      #                  {
                        #     "type": "text",
                        #     "text": " "
                        # },
                        # {
                        #     "type": "emoji",
                        #     "name": emoji_name,
                        # },
                    ]
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "text": date,
                "type": "mrkdwn"
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Word*"
                },
                {
                    "type": "plain_text",
                    "text": random_word
                },
                # {
                #     "type": "mrkdwn",
                #     "text": "*Letter*"
                # },
                # {
                #     "type": "plain_text",
                #     "text": wordle_lotd
                # },
                {
                    "type": "mrkdwn",
                    "text": "*Emoji*"
                },
                {
                    "type": "mrkdwn",
                    "text": f':{emoji_name}:',
                },
                {
                    "type": "mrkdwn",
                    "text": "*wiby*"
                },
                {
                    "type": "mrkdwn",
                    "text": wiby_url,
                },
                {
                    "type": "mrkdwn",
                    "text": "*Song*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"<{song_url}|{song_title}>",
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": today_event_str,
                }
            ]
        }
    ]
    return eddie_blocks
    
    
def get_thread_blocks(slash_text):
    if slash_text == 'abhay' or slash_text == 'smol':
        blocks = get_abhay_blocks()
    else:
        blocks = get_eddie_blocks()
    return {
        "blocks": blocks,
        "response_type": "in_channel",
        "unfurl_links": False,
        "unfurl_media": False
    }


def already_daily_commend_from_today():
    eastern = ZoneInfo("America/New_York")
    today = datetime.now(eastern).date()
    midnight = datetime.combine(today, datetime.min.time())
    today_midnight_timestamp = int(midnight.timestamp())

    response = slack_client.conversations_history(
        channel=GAMES_CHANNEL_ID,
        oldest=today_midnight_timestamp
    )

    for message in response['messages']:
        if 'The Dailies' in message['text']:
            return True

    return False


def lambda_handler(event, context):
    if already_daily_commend_from_today():
        return

    slack_response_url = event['slack_response_url']
    slash_text = event['slack_slash_text']
    
    data = get_thread_blocks(slash_text)
    response = requests.post(
        slack_response_url,
        headers={"Content-Type": "application/json" },
        data=json.dumps(data)
    )
    
    return ''

