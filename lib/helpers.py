# coding=utf-8
import config as cnf
from lib.log import get_log, log_message

import os
import json
import codecs
import time
import glob
from datetime import datetime

from lib.dates import get_dates, get_day_of_week, get_date_type
from get_workers import add_workers

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, get_template_attribute
import pandas as pd
#import modin.pandas as pd

import ast

from functools import wraps

def remove_exemptions (exemptions):
    new_exemptions = {}
    if len(exemptions)>0:
        for name, date in exemptions.items():
            if datetime.strptime(date,'%Y-%m-%d') >= datetime.today():
                new_exemptions[name] = date
    return new_exemptions

def remove_expired_exemptions ():
    users_df = cnf.get_users_df()
    users_df['exemptions'] = users_df['exemptions'].apply(remove_exemptions)
    cnf.update_users_file(users_df)

def get_duty_table_names ():
    filenames = glob.glob('results/*') # * means all if need specific format then *.csv
    filenames.sort(key=os.path.getctime)
    filenames[-1] = f'{filenames[-1]} הכי חדש'
    filenames = [file_name.replace('\\','/') for file_name in filenames]
    filenames = [file_name.split('/')[1] for file_name in filenames]
    return filenames

def new_user_hundle (new_user):
    new_user['weekday_history'] = [{}]
    new_user['weekend_history'] = [{}]
    new_user['last_weekday'] = '2000-01-01'
    new_user['last_weekend'] = '2000-01-01'

    return new_user
