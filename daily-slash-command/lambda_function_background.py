import os
import base64
import urllib.parse
import json

from datetime import datetime, timedelta

import random

import requests

import asyncio
import aiohttp


session = aiohttp.ClientSession()


async def get_wordle_lotd():
    LOTD_URL = 'https://rkigvsdewg.execute-api.us-east-1.amazonaws.com/default/ygyl-python3-9/wordle-lotd'
    async with session.get(LOTD_URL) as response:
    	wordle_lotd = await response.text()
    return wordle_lotd


async def get_random_word():
    wordnik_api_key = os.environ['WORDNIK_API_KEY']
    WORDNIK_URL = f'https://api.wordnik.com/v4/words.json/randomWord?minLength=5&maxLength=5&api_key={wordnik_api_key}'
    async with session.get(WORDNIK_URL) as response:
    	result = await response.json()
    random_word = result['word'].upper()
    return random_word


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
    elif 0 <= year < 1000:
        suffix = ' AD'
    else:
        suffix = ''
    
    return f"On this day {today_event['year']}{suffix}: {today_event['event']}"


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


def get_abhay_blocks():
    def get_date():
        date_time_utc = datetime.now()
        date_time_est = date_time_utc - timedelta(hours=4)
        formatted_date = date_time_est.strftime("%a %-m/%-d/%y")
        return formatted_date

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
							"name": "wordle2"
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
							"name": "mini"
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
		}
    ]
    return abhay_blocks


def get_eddie_blocks():
    def get_date():
        date_time_utc = datetime.now()
        date_time_est = date_time_utc - timedelta(hours=4)
        formatted_date = date_time_est.strftime("%B %d, %Y")
        return formatted_date
    
    date = get_date()
    loop = asyncio.get_event_loop()
    today_event_str, random_word, wordle_lotd = loop.run_until_complete(
    	asyncio.gather(
    		get_today_event_str(),
    		get_random_word(),
    		get_wordle_lotd()
    	)
    )
    
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
							"name": "wordle2"
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
							"name": "mini"
						},
                        {
							"type": "text",
							"text": " "
						},
						{
							"type": "emoji",
							"name": "plusword"
						}
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
					"text": "*Random Word*"
				},
				{
					"type": "plain_text",
					"text": random_word
				},
				{
					"type": "mrkdwn",
					"text": "*LOTD*"
				},
				{
					"type": "plain_text",
					"text": wordle_lotd
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
    return eddie_blocks
    
    
def get_thread_blocks(slash_text):
    if slash_text == 'abhay':
        blocks = get_abhay_blocks()
    else:
        blocks = get_eddie_blocks()
    return {"blocks": blocks, "response_type": "in_channel"}


def lambda_handler(event, context):
    response_url = get_response_url(event)
    slash_text = get_slash_text(event)
    
    data = get_thread_blocks(slash_text)
    response = requests.post(
        response_url,
        headers={"Content-Type": "application/json" },
        data=json.dumps(data)
    )
    
    print(response.status_code)
    print(response.text)
    
    return ''

