from slack_sdk import WebClient

SLACK_BOT_TOKEN = ...

slack_client = WebClient(SLACK_BOT_TOKEN)

response = slack_client.conversations_history(
    channel="C04C5AVUMQF",
    limit=10
)

daily_message = response.data['messages'][0]

response = slack_client.chat_postMessage(
    channel='general',
    text='Hello!',
    thread_ts=daily_message['ts']
)
