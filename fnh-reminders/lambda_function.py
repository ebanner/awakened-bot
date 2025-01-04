from datetime import datetime, timedelta
import os
import json
import urllib.request


TOKEN = os.environ.get("DEV_TOKEN")
DESTINATION_CHANNEL = 'general'


def get_time_est(time):
    # Parse the date string into a datetime object
    date_time_utc = datetime.fromisoformat(time[:-1])  # Remove 'Z' at the end
    
    # Convert UTC datetime to Eastern Time (subtracting 4 hours for EDT)
    date_time_est = date_time_utc - timedelta(hours=4)
    
    # Extract hour and minutes
    hour = date_time_est.hour
    minutes = date_time_est.minute
    
    # Extract day of the week (in terms of names)
    day_of_week = date_time_est.strftime("%A")  # %A for full weekday name

    return (day_of_week, hour, minutes)
    

def http_post(url, data):
    data = urllib.parse.urlencode(tuple(data.items()))
    data = data.encode("ascii")

    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    response = urllib.request.urlopen(request).read().decode('utf-8')
    response_dict = json.loads(response)
    return response_dict


def send_message(channel, text):
    response = http_post(
        'https://slack.com/api/chat.postMessage',
        data={
            'channel': channel,
            'text': text,
            'token': TOKEN,
        }   
    )   
    return response
    
    
def send_weekly_announcement():
    send_message('general', """*This Week's Events:*
Friday Night Hangout 🥳
Friday, May 31st 7:00 PM EST

Come join us for a fun time at Friday Night Hangout!

Every Friday (7:00-9:00pm EST)

Link to join will be posted in #chopping-wood about 10 minutes before the event starts.""")
    
    
def send_day_of_announcement():
    send_message('general', """*Today's Events:*
Friday Night Hangout 🥳
Friday, May 31st 7:00 PM EST

Come join us for a fun time at Friday Night Hangout!

Every Friday (7:00-9:00pm EST)

Link to join will be posted in #chopping-wood about 10 minutes before the event starts.""")


def send_reminder():
    send_message('general', """*Starting Soon:*
Friday Night Hangout 🥳
Friday, May 31st 7:00 PM EST

Come join us for a fun time at Friday Night Hangout!

https://calendar.app.google/bSEfptpaHaVgo6Fb6""")


def lambda_handler(event, context):
    print('EVENT', event)
        
    if 'time' not in event:
        return
    time_utc = event['time']
    day, hour, minute = get_time_est(time_utc)
    
    if ([day, hour] == 'Sunday', 8):
        send_weekly_announcement()
    elif ([day, hour] == 'Friday', 8):
        send_day_of_announcement()
    elif ([hour, minute, day] == 'Friday', 18, 50):
        send_reminder()

