# coding=utf-8
from flask import Flask
from flask import render_template
from flask import request
from flask.json import jsonify
import os
import json
import codecs
import datetime
import pandas as pd
from typing import Any
import config as cnf
from log import getLog
current_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder=os.path.join(current_dir, 'static'))  # Runs the HTML from the static folder
users_file = os.path.join(current_dir, 'db/users.json')
users_df = pd.read_json('db/users.json', encoding='utf-8-sig')
users_df['id'] = users_df['id'].astype('str')

site_log = getLog('Website')
xlsx_log = getLog('XLSX')

import inspect
import sys

def get_func_name():
    return inspect.currentframe().f_back.f_code.co_name

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)


def was_toran_yesterday(the_date, user):
    delta = datetime.datetime.strptime(the_date, '%Y-%m-%d') - datetime.datetime.strptime(user['last_toranut'],
                                                                                          '%Y-%m-%d')
    sofash_delta = datetime.datetime.strptime(the_date, '%Y-%m-%d') - datetime.datetime.strptime(user['last_shabbat'],
                                                                                          '%Y-%m-%d')
    print(delta, sofash_delta)
    return (delta.days < 2) or (sofash_delta.days < 4)


def get_dates_list(dates):
    dates_list = []
    for year in dates:
        y = year
        for month in dates[year]:
            m = month
            for day in dates[year][month]:
                d = day
                dates_list.append(datetime.date(int(y), int(m) + 1, int(d)))
    return dates_list


def day_of_week(days_checked):
    days_list = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
    day_of_week_list = []
    for day in days_checked:
        day_of_week_list.append(days_list[day.weekday()])
    return day_of_week_list


def weekday_or_weekend(dates_list):
    holidays = pd.read_csv('db/holidays.csv')
    dates_type = []
    for date in dates_list:
        if str(date) in holidays.Date.values:
            dates_type.append('holiday: ' + holidays[holidays['Date'] == str(date)]['Name'].iloc[0])
        else:
            dates_type.append('סופש' if date.weekday() in [3, 4, 5] else 'אמצע שבוע')
    return dates_type


def updates_last_toranut(new_date, user_id, is_weekday):
    if is_weekday:
        users_df.loc[users_df['id'] == user_id, ['last_toranut']] = str(new_date)
    else:
        users_df.loc[users_df['id'] == user_id, ['last_shabbat']] = str(new_date)


def is_exempt(toranut, users_data, is_week_day, date):
    """Receives kind of toranut, if its weekday or not, and all of the users and
    returns only the eligible users"""
    available_df = users_data
    for index in range(users_data.shape[0]):
        # recieves a row
        exemptions = users_data.iloc[index]['ptorim']
        if is_week_day:
            exemption = cnf.EXEMPTS_REGULAR[toranut]  # type string
        else:
            exemption = cnf.EXEMPTS_SHABBAT[toranut]  # type: string
        dating = exemptions[exemption]  # type: string
        if dating == '':
            dating = "1998-01-01"

        validation_date = datetime.datetime.strptime(dating, '%Y-%m-%d')
        toranut_date = datetime.datetime.strptime(str(date), '%Y-%m-%d')
        if validation_date > toranut_date or was_toran_yesterday(str(date), users_data.iloc[index]):
            available_df = available_df.drop(index=index)
    return available_df


def get_oldest_toranim(availables, is_weekday):
    """Receives all of the available users and returns the one who had the most time without this toranut"""
    if is_weekday:
        last_date = 'last_toranut'
    else:
        last_date = 'last_shabbat'
    the_chosen = availables[availables[last_date] == availables[last_date].min()].sample(n=1)
    return the_chosen

def gives_day_toran():
    for toranut_name in ['kitchen1', 'kitchen2', 'shmirot1', 'shmirot2']:
        availables = is_exempt(toranut_name, users_df, True, row['dates'])
        chosen_user = get_oldest_toranim(availables, True)
        # writes into sheet
        final_csv.loc[final_csv['dates'] == row['dates'], [toranut_name]] = chosen_user['name'].values[0]
        updates_last_toranut(row['dates'], str(list(chosen_user['id'])[0]), True)

def gives_weekend_toran():
    for toranut_name in ['kitchen1', 'shmirot1']:
        available = is_exempt(toranut_name, users_df, False, row['dates'])

        if index > 0:
            yesterday = final_csv.iloc[index - 1]
            today = final_csv.iloc[index]

            if yesterday['day_status'] == 'אמצע שבוע' and today['day_status'] != 'אמצע שבוע':
                chosen_user = get_oldest_toranim(available, False)
                final_csv.loc[final_csv['dates'] == row['dates'], [toranut_name]] = chosen_user['name'].values[0]
                updates_last_toranut(row['dates'], str(list(chosen_user['id'])[0]), False)

            elif yesterday['day_status'] != 'אמצע שבוע' and today['day_status'] != 'אמצע שבוע':
                final_csv.loc[index: index, [toranut_name]] = yesterday[toranut_name]
                # update user last shabbat
                new_date = row['dates']
                id = str(yesterday[toranut_name])
                users_df.loc[users_df['id'] == id, ['last_shabbat']] = str(new_date)

def gives_toran(final_csv):
    for index, row in final_csv.iterrows():
        if row['day_status'] == 'אמצע שבוע':
            gives_day_toran()
        else:  # סוף שבוע
            gives_weekend_toran()
    return final_csv


def edit_last_json(csv):
    final_users = csv.to_dict('index')
    f2 = []
    for key in final_users:
        f2.append(final_users[key])
    writes_to_json(f2, 'db/users.json')


# =========================== landing page rander ============================
@app.route("/")  # Opens index.html when the user searches for http://127.0.0.1:5000/
def hello():
    usersFile = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))

    site_log.info(f'Function name: {get_func_name()} | message: got users')
    return render_template('index.html', users=usersFile)


# =========================== Add User ================================
@app.route('/addUser', methods=['POST'])  # from mdb-editor2.js
def addUser():
    jsdata = request.form['javascript_data']
    new_user = jsdata.split(',')
    user = {"id": str(new_user[0]), "name": new_user[1], "unit": new_user[2], "last_toranut": '2000-01-01',
            "last_shabbat": '2000-01-01', "ptorim": {'פטור שמירות אמצ"ש': new_user[3], 'פטור שמירות סופ"ש': new_user[4],
                                                     'פטור מטבחים אמצ"ש': new_user[5], 'פטור מטבחים סופ"ש': new_user[6]}}
    new_data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data.append(user)
    writes_to_json(new_data, users_file)

    site_log.info(f'Function name: {get_func_name()} | message: added user to json')
    return '', 204


# =========================== Remove User =============================
@app.route('/removeUser', methods=['POST']) # from mdb-editor2.js
def removeUser():
    jsdata = str(request.form['javascript_data'])
    data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data = []
    for line in data:
        if line['id'] != str(jsdata):
            new_data.append(line)
    writes_to_json(new_data, users_file)

    site_log.info(f'Function name: {get_func_name()} | message: removed user from json')
    return '', 204


# =========================== edit user ===============================
@app.route('/editUser', methods=['POST']) # from mdb-editor2.js
def editUser():
    original_id = request.form['original_id']
    new_user = request.form['new_user']
    new_user = new_user.split(',')
    user = {"id": new_user[0], "name": new_user[1], "unit": new_user[2],
            "ptorim": {'פטור שמירות אמצ"ש': new_user[3], 'פטור שמירות סופ"ש': new_user[4],
                       'פטור מטבחים אמצ"ש': new_user[5], 'פטור מטבחים סופ"ש': new_user[6]}}

    data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data = []
    for line in data:
        if line['id'] != original_id:
            new_data.append(line)
        else:
            user["last_toranut"] = line["last_toranut"]
            user["last_shabbat"] = line["last_toranut"]
            new_data.append(user)

    writes_to_json(new_data, users_file)

    site_log.info(f'Function name: {get_func_name()} | message: updated user in json')
    return '', 204


# =========================== get Exemptions =========================
@app.route('/getPtorim', methods=['POST'])
def getPtorim():
    id = request.form['javascript_data']
    data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    for line in data:
        if line['id'] == id:
            site_log.info(f'Function name: {get_func_name()} | message: got ptorim')
            return jsonify({'ptorim': line['ptorim']})
            # return dict(line['ptorim'])


# =========================== Give final excel ========================
@app.route('/giveExcel', methods=['POST'])
def giveExcel():
    users_df['id'] = users_df['id'].astype('str')
    dates = json.loads(request.form['javascript_data'])
    dates_list = get_dates_list(dates)
    dates_status_list = weekday_or_weekend(dates_list)
    day_of_week_list = day_of_week(dates_list)
    table_content = {'dates': dates_list, 'day_of_week': day_of_week_list, 'day_status': dates_status_list}
    final_csv = pd.DataFrame(table_content,
                             columns=['dates', 'day_of_week', 'day_status', 'kitchen1', 'kitchen2', 'shmirot1',
                                      'shmirot2'])
    final_csv = gives_toran(final_csv)
    file_name = str(dates_list[0]) + '-' + str(dates_list[-1]) + '.csv'
    final_csv.to_csv(file_name, index=False, header=True, encoding='utf_8-sig')
    users_df['id'] = users_df['id'].astype('str')
    # edit_last_json(users_df)''
    xlsx_log.info(f'Function name: {get_func_name()} | message: created an excel file')
    return '', 204


if __name__ == "__main__":
    app.run(debug=True)
