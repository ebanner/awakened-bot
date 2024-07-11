import os
import base64
import urllib.parse
import json

import requests


DAILIES_THREAD_NAME = ":wordle2: :connections2: :mini: :plusword:"


def get_response_url(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    response_url = body_dict['response_url']
    return response_url


def lambda_handler(event, context):
    response_url = get_response_url(event)

    response = requests.post(
        response_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "text": DAILIES_THREAD_NAME,
            "response_type": "in_channel",
        })
    )
    
    return ''
