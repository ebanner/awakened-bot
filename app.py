import os
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")


def get_me():
    return 'U04CYG7MEKB'


def get_author(event):
    return event['user']


def get_reactions(message):
    response = app.client.reactions_get(
        channel=message['channel'],
        timestamp=message['ts'],
    )
    reactions = response.data['message']['reactions']
    return reactions


def get_emoji_name(event):
    emoji_name = event['reaction']
    return emoji_name


def get_users(reaction):
    users = reaction['users']
    return users


def get_reaction(reactions, emoji_name):
    reaction = [reaction for reaction in reactions if reaction['name'] == emoji_name][0]
    return reaction


def tell(channel, text):
    # print(msg)
    result = app.client.chat_postMessage(channel=channel, text=text)
    print(result)

def get_message(event):
    item = event['item']
    assert item['type'] == 'message'
    msg = item

    # message = app.client.conversations_history(
    #     channel=msg['channel'],
    #     latest=msg['ts'],
    #     limit=1,
    # )

    link = app.client.chat_getPermalink(
        channel=msg['channel'],
        message_ts=msg['ts'],
    )
    msg['link'] = link.data['permalink']

    import pprint
    pprint.pprint(msg)

    return msg


def get_destination_channel():
    general_channel = 'C04C5AVUMQF'
    channel = general_channel
    return channel


@app.event("reaction_added")
def handle_reaction_added_event(body, logger):
    event = body['event']
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
    destination_channel = get_destination_channel()
    if me in users:
        tell(destination_channel, message['link'])


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))