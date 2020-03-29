﻿# coding=utf-8
import sys
import config as cnf
from lib.log import get_log, log_message

import os
import json
from datetime import datetime

import pandas as pd
#import modin.pandas as pd

xlsx_log = get_log('XLSX')
users_df = cnf.get_users_df()

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)

def was_toran_yesterday(date, user) -> bool:
    weekday_delta = datetime.strptime(date,'%Y-%m-%d')\
    - datetime.strptime(user['last_weekday'],'%Y-%m-%d')

    weekend_delta = datetime.strptime(date,'%Y-%m-%d')\
    - datetime.strptime(user['last_weekend'],'%Y-%m-%d')

    return (weekday_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKDAY_TORANUTS)\
    or (weekend_delta.days < cnf.MIN_DAYS_BETWEEN_WEEKEND_TORANUTS)

def update_last_toranut_date(new_date, user_id, is_weekday):
    user_mask = users_df['id'] == user_id
    if is_weekday:
        users_df.loc[user_mask, ['last_weekday']] = new_date
    else:
        users_df.loc[user_mask, ['last_weekend']] = new_date

def is_exempt(possible_exemption, user_exemptions, toranut_date):
    if possible_exemption in user_exemptions:
        exemption_date = user_exemptions[possible_exemption]  # type: string
        exemption_date = datetime.strptime(exemption_date, '%Y-%m-%d')
        toranut_date = datetime.strptime(toranut_date, '%Y-%m-%d')
        return exemption_date > toranut_date
    else:
        return False

def get_available_toranim(toranut_name:str, is_week_day:bool, toranut_date:str):
    """Receives kind of toranut, if its weekday or not, and all of the users and
    returns only the eligible users"""
    available_users_df = users_df.copy()
    if is_week_day:
        possible_exemption = cnf.WEEKDAY_TORANUYOT[toranut_name]  # type string
    else:
        possible_exemption = cnf.WEEKEND_TORANUYOT[toranut_name]  # type: string

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
        return chosen_user
    else:
        raise Exception('no available toranim')


def set_weekday_toranim(final_csv, index, row):
    for toranut_name in cnf.WEEKDAY_TORANUYOT.keys():
        available_users_df = get_available_toranim(toranut_name=toranut_name,\
                                                    is_week_day=True,\
                                                    toranut_date=row['date'])

        chosen_user = get_oldest_toran(available_users_df, True)
        # writes into sheet - user name - > date (row)/toranut name (col)
        text_to_fill = f"{chosen_user['name'].values[0]} | {chosen_user['id'].values[0]} | {chosen_user['unit'].values[0]}"
        final_csv.loc[index: index, [toranut_name]] = text_to_fill
        update_last_toranut_date(new_date=row['date'],\
                            user_id=str(list(chosen_user['id'])[0]), is_weekday=True)

def set_weekend_toranim(final_csv, index, row):
    for toranut_name in cnf.WEEKEND_TORANUYOT.keys():
        available_users_df = get_available_toranim(toranut_name=toranut_name,\
                                                    is_week_day=False,\
                                                    toranut_date=row['date'])

        if index > 0:
            yesterday = final_csv.iloc[index - 1]
            today = final_csv.iloc[index]

            # if yesterday and today are weekends setting for today yesterday's toran
            if yesterday['date_type'] == 'סופש':
                final_csv.loc[index: index, [toranut_name]] = yesterday[toranut_name]
                # update user last weekend
                new_date = row['date']
                yesterday_user = yesterday[toranut_name]
                yesterday_user_mask = users_df['id'] == yesterday_user

                users_df.loc[yesterday_user_mask, ['last_weekend']] = new_date
                continue

        # if today is the first day of the weekend, find toran for this weekend
        chosen_user = get_oldest_toran(available_users_df, False)
        text_to_fill = f"{chosen_user['name'].values[0]} | {chosen_user['id'].values[0]} | {chosen_user['unit'].values[0]}"
        final_csv.loc[index: index, [toranut_name]] = text_to_fill
        update_last_toranut_date(row['date'], chosen_user['id'].values[0], False)

def add_toranim(final_csv):
    for index, row in final_csv.iterrows():
        if row['date_type'] == 'אמצש':
            set_weekday_toranim(final_csv, index, row)
        else:
            set_weekend_toranim(final_csv, index, row)
    cnf.update_users_file(users_df)
    return final_csv
