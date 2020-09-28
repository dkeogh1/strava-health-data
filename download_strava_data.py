from stravalib.client import Client
import pandas as pd
# swagger_client.configuration.access_token = 'ea71ebb10e1a191fb24cbce84e5ad843b43a0bcb'

client = Client(access_token='')

activities = client.get_activities()

data = []
for activity in activities:
    my_dict = activity.to_dict()
    data.append(my_dict)

keeper_columns = ['average_speed',
                  'average_heartrate',
                  'average_watts',
                  'distance',
                  'moving_time',
                  'total_elevation_gain',
                  'type',
                  'start_date_local']

df = pd.DataFrame(data)
df = df[keeper_columns]

df.to_csv('stravadata.csv')

# https://yizeng.me/2017/01/11/get-a-strava-api-access-token-with-write-permission/
# http: // www.strava.com/oauth/authorize?client_id = 54076 & response_type = code & redirect_uri = http: // localhost/exchange_token & approval_prompt = force & scope = read_all, profile: read_all, activity: read_all
