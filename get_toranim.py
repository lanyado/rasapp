# coding=utf-8
import config as cnf
from lib.log import getLog

import os
import json
import datetime
import inspect

#import pandas as pd
import modin.pandas as pd
#from typing import Any

current_dir = os.path.dirname(os.path.realpath(__file__))

xlsx_log = getLog('XLSX')

users_df = pd.read_json('db/users.json', encoding='utf-8-sig')
users_df['id'] = users_df['id'].astype('str')


def get_func_name():
    return inspect.currentframe().f_back.f_code.co_name

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)

def was_toran_yesterday(date, user):
    weekday_delta = datetime.datetime.strptime(date,'%Y-%m-%d')\
    - datetime.datetime.strptime(user['last_toranut'],'%Y-%m-%d')

    weekend_delta = datetime.datetime.strptime(date,'%Y-%m-%d')\
    - datetime.datetime.strptime(user['last_weekend'],'%Y-%m-%d')

    return (weekday_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKDAY_TORANUTS)\
    or (weekend_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKEND_TORANUTS)

def update_last_toranut(new_date, user_id, is_weekday):
    if is_weekday:
        users_df.loc[users_df['id'] == user_id, ['last_toranut']] = str(new_date)
    else:
        users_df.loc[users_df['id'] == user_id, ['last_weekend']] = str(new_date)

def is_exempt(possible_exemptions, user_exemptions, toranut_date):
    exemption_date = user_exemptions[possible_exemptions]  # type: string
    if exemption_date == '':
        exemption_date = "1998-01-01"

    exemption_date = datetime.datetime.strptime(exemption_date, '%Y-%m-%d')
    toranut_date = datetime.datetime.strptime(toranut_date, '%Y-%m-%d')
    return exemption_date > toranut_date

def get_available_toranim(toranut, users_df, is_week_day, toranut_date):
    """Receives kind of toranut, if its weekday or not, and all of the users and
    returns only the eligible users"""
    available_df = users_df
    toranut_date = str(toranut_date)
    if is_week_day:
        possible_exemptions = cnf.EXEMPTS_WEEKDAY[toranut]  # type string
    else:
        possible_exemptions = cnf.EXEMPTS_WEEKEND[toranut]  # type: string

    for index, user in users_df.iterrows():
        # recieves a row
        user_exemptions = user['ptorim']

        if is_exempt(possible_exemptions, user_exemptions, toranut_date)\
         or was_toran_yesterday(toranut_date, user):
            available_df.drop(index=index, inplace = True)
    return available_df


def get_oldest_toranim(availables, is_weekday):
    """Receives all of the available users and returns the one who had the most time without this toranut"""
    if is_weekday:
        last_date = 'last_toranut'
    else:
        last_date = 'last_weekend'

    mask = availables[last_date] == availables[last_date].min()
    if len(availables[mask])>0:
        chosen_user = availables[mask].sample(n=1)
        return chosen_user
    else:
        print('no available toranim')

def gives_day_toran(final_csv, index, row):
    for toranut_name in ['kitchen1', 'kitchen2', 'shmirot1', 'shmirot2']:
        availables = get_available_toranim(toranut=toranut_name, users_df=users_df,\
                                is_week_day=True, toranut_date=row['date'])
        chosen_user = get_oldest_toranim(availables, True)
        # writes into sheet
        final_csv.loc[final_csv['date'] == row['date'], [toranut_name]] = chosen_user['name'].values[0]
        update_last_toranut(new_date=row['date'], user_id=str(list(chosen_user['id'])[0]), is_weekday=True)

def give_weekend_toran(final_csv, index, row):
    for toranut_name in ['kitchen1', 'shmirot1']:
        available = get_available_toranim(toranut=toranut_name, users_df=users_df,\
                                is_week_day=False, toranut_date=row['date'])

        if index > 0:
            yesterday = final_csv.iloc[index - 1]
            today = final_csv.iloc[index]

            if yesterday['date_type'] == 'אמצע שבוע' and today['date_type'] != 'אמצע שבוע':
                chosen_user = get_oldest_toranim(available, False)
                final_csv.loc[final_csv['date'] == row['date'], [toranut_name]] = chosen_user['name'].values[0]
                update_last_toranut(row['date'], str(list(chosen_user['id'])[0]), False)

            elif yesterday['date_type'] != 'אמצע שבוע' and today['date_type'] != 'אמצע שבוע':
                final_csv.loc[index: index, [toranut_name]] = yesterday[toranut_name]
                # update user last weekend
                new_date = row['date']
                id = str(yesterday[toranut_name])
                users_df.loc[users_df['id'] == id, ['last_weekend']] = str(new_date)

def add_toranim(final_csv):
    for index, row in final_csv.iterrows():
        if row['date_type'] == 'אמצע שבוע':
            gives_day_toran(final_csv, index, row)
        else:  # סוף שבוע
            give_weekend_toran(final_csv, index, row)
    return final_csv
