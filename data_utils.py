import os
import json

import pandas as pd

from stravalib.client import Client


class FitbitDataHandler():

    def __init__(self, sleep_df=None, heart_rate_df=None, sleep_dir=None, columns=['date','deep','wake','light','rem']):
        self.sleep_dir = sleep_dir
        self.sleep_df = sleep_df
        self.heart_rate_df = heart_rate_df
        self.columns = columns

    def generate_file_list(self):
        sleep_jsons = []
        for root, dirs, files in os.walk(self.sleep_dir):
            for name in files:
                file = os.path.join(root, name)
                if 'json' in file:
                    sleep_jsons.append(os.path.join(root, name)) 
            for name in dirs:
                print(os.path.join(root, name))
        return sleep_jsons

    def _extract_fitbit_sleep(self, sleep_files):
        sleep_info = []
        for j in sleep_files:
            f = json.load(open(j,'r'))
            for s in f:
                if s['mainSleep']:
                    try:
                        date_dict = {}
                        for i in s: 
                            if i == 'dateOfSleep':
                                date_dict['date'] = s[i]
                            elif i =='levels':
                                date_dict['deep'] = s[i]['summary']['deep']['minutes']
                                date_dict['wake'] = s[i]['summary']['wake']['minutes']
                                date_dict['light'] = s[i]['summary']['light']['minutes']
                                date_dict['rem'] = s[i]['summary']['rem']['minutes']
                        sleep_info.append(date_dict)
                    except:
                        KeyError

        return sleep_info

    def initialize_hr_df(self):
        self.heart_rate_df = pd.read_csv(self.heart_rate_df)
        self.heart_rate_df['date'] = pd.to_datetime(self.sleep_df['date'])
        self.heart_rate_df.sort_values(by='date', inplace=True)
        self.heart_rate_df['date'] = self.heart_rate_df['date'].astype('str')
        self.heart_rate_df = self.heart_rate_df[['date','overall_score', 'resting_heart_rate']]

    def load_sleep_df(self, sleep_jsons):
        sleep_data = self._extract_fitbit_sleep(sleep_jsons)
        sleep_df = pd.DataFrame(data=sleep_data,columns=self.columns)
        sleep_df['date'] = pd.to_datetime(sleep_df['date'])
        sleep_df.sort_values(by='date', inplace=True)
        sleep_df['date'] = sleep_df['date'].astype('str')
        self.sleep_df = sleep_df


class StravaDataHandler():

    def __init__(self, api_key=None, csv_path=None, df=None):
        self.api_key = api_key
        self.csv_path = csv_path
        self.df = df

        if self.api_key:
            self.client = Client(access_token=self.api_key)

    def pull_strava_activities(self, keeper_columns):
        activities = self.client.get_activities()
        return activities

    def csv_to_df(self):
        self.df = pd.read_csv(self.csv_path)
        
        if 'Unnamed: 0' in self.df.columns:
            self.df.drop(columns=['Unnamed: 0'], inplace=True)

    def batch_to_df(self, events, keeper_columns):
        data = []
        for activity in events:
            my_dict = activity.to_dict()
            data.append(my_dict)
        
        if len(keeper_columns) > 0:
            self.df = pd.DataFrame(data)
            self.df = self.df[keeper_columns]
        else:
            self.df = pd.DataFrame(data)

    def _convert_str_to_second(self, time):
        h, m, s = time.split(':')
        h = int(h)
        m = int(m)
        s = int(s)
        totalseconds = (h*3600) + (m*60) + (s)
        return totalseconds

    def _get_minutes(self, time):
        h, m, s = time.split(':') 
        total_min = int(h)*60+int(m)+int(s)/60
        return int(total_min)

    def generate_total_times(self, time_column):
        if time_column in self.df.columns:
            try:
                self.df['total_seconds'] = self.df[time_column].apply(lambda x: self._convert_str_to_second(x))
                self.df['total_minutes'] = self.df[time_column].apply(lambda x: self._get_minutes(x))
            except Exception as e:
                print(e)
        
        else:
            print('Provided column not in df')

    def convert_from_metric(self):
        self.df['distance'] = self.df['distance']/1609.34
        self.df['average_speed'] = self.df['average_speed'] * 2.23694
        self.df['average_speed']  = self.df['average_speed'].round(2)
        self.df['miles/sec'] = self.df['distance']/self.df['total_seconds']
        self.df['miles/hr'] = self.df['miles/sec']*3600
    
    def date_to_str(self):
        self.df['date'] = pd.to_datetime(self.df['start_date_local']).dt.date
        self.df['date'] = self.df['date'].astype('str')

    def mask_df(self, mask_columns=[]):
        self.df = self.df[mask_columns]

    def subset_by_type(self, activities=[]):
        self.df = self.df [self.df ['type'].isin(activities)]

