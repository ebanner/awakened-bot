import os
import json
import urllib.request

TOKEN = os.environ.get("SLACK_BOT_TOKEN")


def http_post(url, data):
    data = urllib.parse.urlencode(tuple(data.items()))
    data = data.encode("ascii")

    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    response = urllib.request.urlopen(request).read().decode('utf-8')
    response_dict = json.loads(response)
    return response_dict


def get_me():
    return 'U04CYG7MEKB'


def get_author(event):
    return event['user']


def get_message(event):
    item = event['item']
    assert item['type'] == 'message'
    msg = item

    # message = app.client.conversations_history(
    #     channel=msg['channel'],
    #     latest=msg['ts'],
    #     limit=1,
    # )

    response = http_post(
        'https://slack.com/api/chat.getPermalink',
        data={
            'token': TOKEN,
            'channel': msg['channel'],
            'message_ts': msg['ts'],
        }
    )
    msg['link'] = response['permalink']
    return msg


def get_emoji_name(event):
    emoji_name = event['reaction']
    return emoji_name


def get_reactions(message):
    response = http_post(
        'https://slack.com/api/reactions.get',
        data={
            'token': TOKEN,
            'channel': message['channel'],
            'timestamp': message['ts'],
        }
    )

    reactions = response['message']['reactions']
    return reactions


def get_reaction(reactions, emoji_name):
    reaction = [reaction for reaction in reactions if reaction['name'] == emoji_name][0]
    return reaction


def get_users(reaction):
    users = reaction['users']
    return users


def get_destination_channel():
    general_channel = 'C04C5AVUMQF'
    channel = general_channel
    return channel


def tell(channel, text):
    response = http_post(
        'https://slack.com/api/chat.postMessage',
        data={
            'channel': channel,
            'text': text,
            'token': TOKEN,
        }
    )
    return response
    

def get_request(lambda_event):
    body = lambda_event.get("body")
    if body is None:
        return None
    else:
        request = json.loads(body)
        return request
    

def lambda_handler(event, context):
    print(json.dumps(event))
    lambda_event = event
    req = get_request(lambda_event)
    print(json.dumps(req))
    
    #
    # Random GET request and the like
    #
    if req is None:
        return {
            'statusCode': 200
        }
    
    #
    # Slack application endpoint check
    #
    if 'challenge' in req:
        challenge_answer = req["challenge"]
        return {
            'statusCode': 200,
            'body': challenge_answer,
        } 

    event = req.get('event', {})
    if event.get('type') != 'reaction_added':
        return {}

    author = get_author(event)
    me = get_me()
    # if author == me:
    #     return

    message, emoji_name = get_message(event), get_emoji_name(event)
    reactions = get_reactions(message)
    reaction = get_reaction(reactions, emoji_name)
    users = get_users(reaction)
    if me not in users:
        return

    tell(channel=me, text=message['link'])

    return {
        'statusCode': 200,
        'challenge': event.get('challenge')
    }

