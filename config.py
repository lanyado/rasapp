import pandas as pd
import os


WEEKDAY_DUTIES = {
    'kitchen1': "פטור מטבחים אמצש",
    'kitchen2': "פטור מטבחים אמצש",
    'shmirot1': "פטור שמירות אמצש",
    'shmirot2': "פטור שמירות אמצש"
}

WEEKEND_DUTIES = {
    'kitchen1': "פטור מטבחים סופש",
    'shmirot1': "פטור שמירות סופש"
}

MIN_DAYS_BETWEEN_WEEKDAY_DUTIES = 2
MIN_DAYS_BETWEEN_WEEKEND_DUTIES = 4

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
USERS_JSON_FILE = os.path.join(CURRENT_DIR, 'db/users.json')

def get_users_df():
    return pd.read_json('db/users.json', encoding='utf-8-sig',\
                       dtype={'id':'str', 'name':'str', 'unit':'str',\
                              'exemptions': 'dict', 'last_weekday': 'str',
                              'last_weekend': 'str'})

def update_users_file(df):
    """Takes data to write and puts it in the file"""
    with open(USERS_JSON_FILE, 'w', encoding='utf-8') as users_file:
        df.to_json(users_file, force_ascii=False, orient='records')