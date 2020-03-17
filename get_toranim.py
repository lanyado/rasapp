# coding=utf-8
import sys
import config as cnf
from lib.log import get_log, log_message

import os
import json
import datetime

import pandas as pd
#import modin.pandas as pd

current_dir = os.path.dirname(os.path.realpath(__file__))

xlsx_log = get_log('XLSX')

users_df = pd.read_json('db/users.json', encoding='utf-8-sig',\
                        dtype={'id':'str', 'name':'str', 'unit':'str',\
                               'exemptions': 'dict', 'last_weekday': 'str',
                               'last_weekend': 'str'})

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)

def was_toran_yesterday(date, user) -> bool:
    weekday_delta = datetime.datetime.strptime(date,'%Y-%m-%d')\
    - datetime.datetime.strptime(user['last_weekday'],'%Y-%m-%d')

    weekend_delta = datetime.datetime.strptime(date,'%Y-%m-%d')\
    - datetime.datetime.strptime(user['last_weekend'],'%Y-%m-%d')

    return (weekday_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKDAY_TORANUTS)\
    or (weekend_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKEND_TORANUTS)

def update_last_toranut_date(new_date, user_id, is_weekday):
    if is_weekday:
        users_df.loc[users_df['id'] == user_id, ['last_weekday']] = new_date
    else:
        users_df.loc[users_df['id'] == user_id, ['last_weekend']] = new_date

def is_exempt(possible_exemption, user_exemptions, toranut_date):
    if possible_exemption in user_exemptions:
        exemption_date = user_exemptions[possible_exemption]  # type: string
        exemption_date = datetime.datetime.strptime(exemption_date, '%Y-%m-%d')
        toranut_date = datetime.datetime.strptime(toranut_date, '%Y-%m-%d')
        return exemption_date > toranut_date
    else:
        return False

def get_available_toranim(toranut_name:str, users_df:pd.DataFrame, is_week_day:bool, toranut_date:str):
    """Receives kind of toranut, if its weekday or not, and all of the users and
    returns only the eligible users"""
    available_users_df = users_df
    if is_week_day:
        possible_exemption = cnf.EXEMPTS_WEEKDAY[toranut_name]  # type string
    else:
        possible_exemption = cnf.EXEMPTS_WEEKEND[toranut_name]  # type: string

    for index, user in users_df.iterrows():
        # user is a row in users_df
        user_exemptions = user['exemptions']

        if is_exempt(possible_exemption, user_exemptions, toranut_date)\
           or was_toran_yesterday(toranut_date, user):
           available_users_df.drop(index=index, inplace = True)
    return available_users_df


def get_oldest_toran(available_users_df, is_weekday):
    """Receives all of the available users and returns the one who had the most time without this toranut"""
    if is_weekday:
        last_date = 'last_weekday'
    else:
        last_date = 'last_weekend'

    mask = available_users_df[last_date] == available_users_df[last_date].min()
    if len(available_users_df[mask])>0:
        chosen_user = available_users_df[mask].sample(n=1)
        print(chosen_user)
        return chosen_user
    else:
        print('no available toranim')
        sys.exit(0)

def set_weekday_toran(final_csv, index, row):
    for toranut_name in ['kitchen1', 'kitchen2', 'shmirot1', 'shmirot2']:
        available_users_df = get_available_toranim(toranut_name=toranut_name, users_df=users_df,\
                                            is_week_day=True, toranut_date=row['date'])
        chosen_user = get_oldest_toran(available_users_df, True)
        # writes into sheet - user name - > date (row)/toranut name (col)
        final_csv.loc[final_csv['date'] == row['date'], [toranut_name]] = chosen_user['name'].values[0]
        update_last_toranut_date(new_date=row['date'],\
                            user_id=str(list(chosen_user['id'])[0]), is_weekday=True)

def set_weekend_toran(final_csv, index, row):
    for toranut_name in ['kitchen1', 'shmirot1']:
        available_users_df = get_available_toranim(toranut_name=toranut_name, users_df=users_df,\
                                                    is_week_day=False, toranut_date=row['date'])

        if index > 0:
            yesterday = final_csv.iloc[index - 1]
            today = final_csv.iloc[index]
            
            # if yesterday and today are weekends setting for today yesterday's toran
            if yesterday['date_type'] == 'סופש':
                final_csv.loc[index: index, [toranut_name]] = yesterday[toranut_name]
                # update user last weekend
                new_date = row['date']
                id = yesterday[toranut_name]
                users_df.loc[users_df['id'] == id, ['last_weekend']] = new_date
                continue
                
        # if today is the first day of the weekend, find toran for this weekend
        chosen_user = get_oldest_toran(available_users_df, False)
        final_csv.loc[index: index, [toranut_name]] = chosen_user['name'].values[0]
        update_last_toranut_date(row['date'], chosen_user['id'].values[0], False)

def add_toranim(final_csv):
    for index, row in final_csv.iterrows():
        if row['date_type'] == 'אמצש':
            set_weekday_toran(final_csv, index, row)
        else:
            set_weekend_toran(final_csv, index, row)
    return final_csv
