import boto3
import time

import pandas as pd


cloudwatch_client = boto3.client('logs')


def get_logs():
    log_group_name = '/aws/lambda/daily-slash-command-test'
    query_string = """
    fields @timestamp, slashCommand, slashText, userId, userName, channelId, channelName
    | filter eventName = "DailySlashCommand"
    | sort @timestamp desc
    | limit 10000
    """
    start_time = int((time.time() - 3600) * 1000)  # Start time (1 hour ago)
    end_time = int(time.time() * 1000)  # End time (current time)

    response = cloudwatch_client.start_query(
        logGroupName=log_group_name,
        startTime=start_time,
        endTime=end_time,
        queryString=query_string
    )

    query_id = response['queryId']

    while True:
        query_response = cloudwatch_client.get_query_results(queryId=query_id)
        if query_response['status'] == 'Complete':
            break
        time.sleep(1)

    results = query_response['results']
    logs = results

    return logs


def get_df(logs):
    results = logs
    def get_timestamp(result):
        for entry in result:
            if entry['field'] == '@timestamp':
                timestamp = entry['value']
                return timestamp

    def get_slash_command(result):
        for entry in result:
            if entry['field'] == 'slashCommand':
                timestamp = entry['value']
                return timestamp

    def get_slash_text(result):
        for entry in result:
            if entry['field'] == 'slashText':
                timestamp = entry['value']
                return timestamp

    def get_user_id(result):
        for entry in result:
            if entry['field'] == 'userId':
                timestamp = entry['value']
                return timestamp

    def get_user_name(result):
        for entry in result:
            if entry['field'] == 'userName':
                timestamp = entry['value']
                return timestamp

    def get_channel_id(result):
        for entry in result:
            if entry['field'] == 'channelId':
                timestamp = entry['value']
                return timestamp

    def get_channel_name(result):
        for entry in result:
            if entry['field'] == 'channelName':
                timestamp = entry['value']
                return timestamp

    rows = []
    for result in results:
        ts = get_timestamp(result)
        slash_command = get_slash_command(result)
        slash_text = get_slash_text(result)
        user_id = get_user_id(result)
        user_name = get_user_name(result)
        channel_id = get_channel_id(result)
        channel_name = get_channel_name(result)

        row = (ts, slash_command, slash_text, user_id, user_name, channel_id, channel_name)
        rows.append(row)


    columns = ['timestamp', 'slash_command', 'slash_text', 'user_id', 'user_name', 'channel_id', 'channel_name']
    df = pd.DataFrame(rows, columns=columns)
    return df


if __name__ == '__main__':
    logs = get_logs()
    df = get_df(logs)
    print(df)

