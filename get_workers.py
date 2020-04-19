# coding=utf-8
import sys
import config as cnf
from lib.log import get_log, log_message

import os
import json
from datetime import datetime
import ast

import pandas as pd
#import modin.pandas as pd

xlsx_log = get_log('XLSX')
users_df = cnf.get_users_df()

def update_user_duties (user_id, date, duty_name, is_weekday):
    user_mask = users_df['id'] == user_id
    if is_weekday:
        history_dict = 'weekday_history'
        last_duty = 'last_weekday'
    else:
        history_dict = 'weekend_history'
        last_duty = 'last_weekend'

    try:
        duties_history = ast.literal_eval(users_df[user_mask][history_dict].values[0])
    except:
        duties_history = users_df[user_mask][history_dict].values[0]

    # update duties history
    duties_history[date] = duty_name
    users_df.loc[user_mask, [history_dict]] = [duties_history]
    # update last duty
    users_df.loc[user_mask, [last_duty]] = date

def was_worker_yesterday(date, user) -> bool:
    weekday_delta = datetime.strptime(date,'%Y-%m-%d')\
    - datetime.strptime(user['last_weekday'],'%Y-%m-%d')

    weekend_delta = datetime.strptime(date,'%Y-%m-%d')\
    - datetime.strptime(user['last_weekend'],'%Y-%m-%d')

    return (weekday_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKDAY_DUTIES)\
    or (weekend_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKEND_DUTIES)

def is_exempt(possible_exemption, user_exemptions, duty_date):
    if possible_exemption in user_exemptions:
        exemption_date = user_exemptions[possible_exemption]  # type: string
        exemption_date = datetime.strptime(exemption_date, '%Y-%m-%d')
        duty_date = datetime.strptime(duty_date, '%Y-%m-%d')
        return exemption_date > duty_date
    else:
        return False

def get_available_workers(duty_name:str, is_week_day:bool, duty_date:str):
    """Receives kind of duty, if its weekday or not, and all of the users and
    returns only the eligible users"""
    available_users_df = users_df.copy()
    if is_week_day:
        possible_exemption = cnf.WEEKDAY_DUTIES[duty_name]  # type string
    else:
        possible_exemption = cnf.WEEKEND_DUTIES[duty_name]  # type: string

    for index, user in users_df.iterrows():
        # user is a row in users_df
        user_exemptions = user['exemptions']

        if is_exempt(possible_exemption, user_exemptions, duty_date)\
           or was_worker_yesterday(duty_date, user):
           available_users_df.drop(index=index, inplace = True)
    return available_users_df


def get_oldest_worker(available_users_df, is_weekday):
    """Receives all of the available users and returns the one who had the most time without this duty"""
    if is_weekday:
        last_date = 'last_weekday'
    else:
        last_date = 'last_weekend'

    mask = available_users_df[last_date] == available_users_df[last_date].min()
    if len(available_users_df[mask])>0:
        chosen_user = available_users_df[mask].sample(n=1)
        return chosen_user
    else:
        raise Exception('No available workers')


def set_weekday_workers(final_csv, index, row):
    for duty_name in cnf.WEEKDAY_DUTIES.keys():
        available_users_df = get_available_workers(duty_name=duty_name,\
                                                    is_week_day=True,\
                                                    duty_date=row['date'])

        chosen_user = get_oldest_worker(available_users_df, True)
        user_id = chosen_user['id'].values[0]
        # writes into sheet - user name - > date (row)/duty name (col)
        text_to_fill = f"{chosen_user['name'].values[0]} | {user_id} | {chosen_user['unit'].values[0]}"
        final_csv.loc[index: index, [duty_name]] = text_to_fill
        #update_last_duty_date(new_date=row['date'],user_id=str(list(user_id), is_weekday=True))
        update_user_duties(user_id, row['date'], duty_name, True)

def set_weekend_workers(final_csv, index, row):
    for duty_name in cnf.WEEKEND_DUTIES.keys():
        available_users_df = get_available_workers(duty_name=duty_name,\
                                                    is_week_day=False,\
                                                    duty_date=row['date'])

        if index > 0:
            yesterday = final_csv.iloc[index - 1]
            #today = final_csv.iloc[index]

            # if yesterday and today are weekends setting for today yesterday's worker
            if yesterday['date_type'] == 'סופש':
                final_csv.loc[index: index, [duty_name]] = yesterday[duty_name]
                # update user last weekend
                new_date = row['date']
                yesterday_user = yesterday[duty_name]
                yesterday_user_mask = users_df['id'] == yesterday_user

                users_df.loc[yesterday_user_mask, ['last_weekend']] = new_date
                continue

        # if today is the first day of the weekend, find worker for this weekend
        chosen_user = get_oldest_worker(available_users_df, False)
        user_id = chosen_user['id'].values[0]
        text_to_fill = f"{chosen_user['name'].values[0]} | {user_id} | {chosen_user['unit'].values[0]}"
        final_csv.loc[index: index, [duty_name]] = text_to_fill
        #update_last_duty_date(row['date'], user_id, False)
        update_user_duties(user_id, row['date'], duty_name, False)

def add_workers(final_csv):
    for index, row in final_csv.iterrows():
        if row['date_type'] == 'אמצש':
            set_weekday_workers(final_csv, index, row)
        else:
            set_weekend_workers(final_csv, index, row)
    cnf.update_users_file(users_df)
    return final_csv
