import os
import base64
import urllib.parse
import json

import requests

from datetime import datetime, timedelta

import random


def get_random_word():   
    wordnik_api_key = os.environ['WORDNIK_API_KEY']
    response = requests.get(f'https://api.wordnik.com/v4/words.json/randomWord?minLength=5&maxLength=5&api_key={wordnik_api_key}')
    result = response.json()
    random_word = result['word'].upper()
    return random_word


def get_date():
    date_time_utc = datetime.now()
    
    # Convert UTC datetime to Eastern Time (subtracting 4 hours for EDT)
    date_time_est = date_time_utc - timedelta(hours=4)
    
    formatted_date = date_time_est.strftime("%B %d, %Y")
    
    return formatted_date
    
    
def get_day():
    date_time_utc = datetime.now()
    date_time_est = date_time_utc - timedelta(hours=4)
    return date_time_est.month, date_time_est.day


def get_today_event_str():
    month, day = get_day()
    api_url = 'https://api.api-ninjas.com/v1/historicalevents?month={}&day={}'.format(month, day)
    response = requests.get(api_url, headers={'X-Api-Key': os.environ['API_NINJAS_KEY']})
    today_events = response.json()
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
    
    
def get_thread_blocks():
    date = get_date()
    today_event_str = get_today_event_str()
    random_word = get_random_word()
    
    blocks = [
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
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": date
				},
				{
					"type": "mrkdwn",
					"text": today_event_str,
				} if slash_text == 'event' else ,
				{
					"type": "mrkdwn",
					"text": f'Random word: {random_word}',
				},
			]
		}
    ]
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
    
    return text
