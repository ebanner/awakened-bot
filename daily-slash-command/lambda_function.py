import os
import base64
import urllib.parse
import json

import requests


def get_response_url(event):
    body_base64_encoded = event['body']
    body_bytes = base64.b64decode(body_base64_encoded)
    body_decoded = body_bytes.decode('utf-8')
    body_dict = dict(urllib.parse.parse_qsl(body_decoded))
    response_url = body_dict['response_url']
    return response_url


def lambda_handler(event, context):
    response_url = get_response_url(event)
    
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "text": ":wordle2: :connections2: :mini: :plusword:",
        "response_type": "in_channel",
    }
    response = requests.post(response_url, headers=headers, data=json.dumps(data))
    
    print(response.status_code)
    print(response.text)
    
    return ''
