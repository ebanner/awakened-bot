from flask import Flask, request
import os
import json
import urllib.request


app = Flask(__name__)

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
    # return 'U04CYG7MEKB' # Edward's Slackbot Dev Workspace
    return 'U02780B5563' # awakened


def get_subscribed_users():
    global SUBSCRIBED_USERS
    return SUBSCRIBED_USERS


def get_reactor(event):
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


def process_emoji_changed(event):
    emoji_name = event['name']
    tell('chopping-wood', f'New emoji! :{emoji_name}:')


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
