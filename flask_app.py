from flask import Flask, request
import os
import sys
import json
import urllib.request

import logging
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

from dotenv import load_dotenv
load_dotenv()


TOKEN = os.environ.get("DEV_TOKEN")
DESTINATION_CHANNEL = 'general'

SUBSCRIBED_USERS = [
    'U04CYG7MEKB' # @edward.banner (Edward's Slackbot Dev Workspace)
]


app = Flask(__name__)


def http_post(url, data):
    data = urllib.parse.urlencode(tuple(data.items()))
    data = data.encode("ascii")

    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    response = urllib.request.urlopen(request).read().decode('utf-8')
    response_dict = json.loads(response)
    return response_dict


def get_me():
    return 'U04CYG7MEKB' # Edward's Slackbot Dev Workspace


def get_subscribed_users():
    global SUBSCRIBED_USERS
    return SUBSCRIBED_USERS


def get_reactor(event):
    return event['user']


def get_channel(event):
    item = event['item']
    assert item['type'] == 'message'
    msg = item
    return msg['channel']


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


def get_reaction(message, emoji_name):
    response = http_post(
        'https://slack.com/api/reactions.get',
        data={
            'token': TOKEN,
            'channel': message['channel'],
            'timestamp': message['ts'],
        }
    )
    reactions = response['message']['reactions']
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


def get_author_name(author_id):
    # result = http_post(
    #     'https://slack.com/api/users.info',
    #     data={
    #         'token': TOKEN,
    #         'user': author_id,
    #     }
    # )
    # return result['user']['name']
    return f'<@{author_id}>'


def get_text(author_name, emoji_name, link):
    return f'{author_name} <{link}|:{emoji_name}:>'


def get_reaction_author(event):
    message, emoji_name = get_message(event), get_emoji_name(event)
    reaction = get_reaction(message, emoji_name)
    users = get_users(reaction)
    return users[0]


def tell_subscribed_user(subscribed_user, event):
    message, emoji_name = get_message(event), get_emoji_name(event)
    reactor = get_reactor(event)
    reactor_name = get_author_name(reactor)
    logging.info(
        'AddedToYourEmojiEvent',
        extra={
            'author': subscribed_user,
            'reactor': reactor,
            'emoji': emoji_name,
            'channel': get_channel(event),
        }
    )
    message = get_text(reactor_name, emoji_name, message['link'])
    tell(channel=subscribed_user, text=message)
    return {
        'statusCode': 200,
        'challenge': event.get('challenge')
    }


def process_reaction_added(event):
    for subscribed_user in get_subscribed_users():
        reactor = get_reactor(event)
        reaction_author = get_reaction_author(event)
        if reaction_author == subscribed_user and reactor != subscribed_user:
            tell_subscribed_user(subscribed_user, event)
            break


def process_emoji_added(event):
    emoji_name = event['name']
    tell(DESTINATION_CHANNEL, f'New emoji added!')
    tell(DESTINATION_CHANNEL, f'`:{emoji_name}:`')
    tell(DESTINATION_CHANNEL, f':{emoji_name}:')


def process_alias_added(event):
    pass
    # alias_name = event['name']
    # emoji_name = event['value'].lstrip('alias:')
    # tell(DESTINATION_CHANNEL, f'New alias added!')
    # tell(DESTINATION_CHANNEL, f'`:{alias_name}:` → `:{emoji_name}:`')
    # tell(DESTINATION_CHANNEL, f':{emoji_name}:')


def is_emoji_added_event(event):
    return event['value'].startswith('https://')


def is_alias_added_event(event):
    return event['value'].startswith('alias:')


def process_emoji_changed(event):
    if is_emoji_added_event(event):
        process_emoji_added(event)
    elif is_alias_added_event(event):
        process_alias_added(event)
    else:
        raise Exception('UNKNOWN EMOJI CHANGED EVENT')


@app.route("/slack/events", methods=['POST'])
def respond_to_event():
    req = request.json

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
    event_type = event.get('type')
    if event_type == 'reaction_added':
        process_reaction_added(event)
    elif event_type == 'emoji_changed':
        process_emoji_changed(event)
    else:
        raise Exception('UNKNOWN EVENT')

    return {
        'statusCode': 200,
        'challenge': event.get('challenge')
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
