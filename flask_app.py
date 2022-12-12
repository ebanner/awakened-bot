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


@app.route("/slack/events", methods=['POST'])
def respond_to_event():
    event = request.json.get('event', {})
    if event.get('type') != 'reaction_added':
        return {}

    print(event)
    import pprint
    pprint.pprint(event)

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
        'challenge': event.get('challenge')
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)