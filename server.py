# coding=utf-8
import config as cnf
from lib.log import get_log, log_message

import os
import json
import codecs
import time

from lib.dates import get_dates, get_day_of_week, get_date_type
from get_toranim import add_toranim

from flask import Flask, render_template, request, jsonify
import pandas as pd
import ast

#import modin.pandas as pd
#from typing import Any

current_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder=os.path.join(current_dir, 'static'))  # Runs the HTML from the static folder
users_json_file = os.path.join(current_dir, 'db/users.json')
#exemptions_file = os.path.join(current_dir, 'db/exemptions.csv')

site_log = get_log('Website')
xlsx_log = get_log('XLSX')

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)

def update_users_file(df):
    """Takes data to write and puts it in the file"""
    with open(users_json_file, 'w', encoding='utf-8') as users_file:
        df.to_json(users_file, force_ascii=False, orient='records')

def edit_last_json(csv):
    final_users = csv.to_dict('index')
    f2 = []
    for key in final_users:
        f2.append(final_users[key])
    writes_to_json(f2, 'db/users.json')

# =========================== landing page rander ============================
@app.route("/")  # Opens index.html when the user searches for http://127.0.0.1:5000/
def hello():
    #users_df = pd.read_json(users_json_file)
    #exemptions_df = pd.read_csv(exemptions_file)
    users = json.load(codecs.open(users_json_file, 'r', 'utf-8-sig'))

    site_log.info(log_message('got users'))
    return render_template('index.html', users=users)

# =========================== Add User ================================
@app.route('/addUser', methods=['POST'])
def addUser():
    new_user = request.form.to_dict()
    new_user['exemptions'] = ast.literal_eval(new_user['exemptions'])

    users_df = cnf.USERS_DF

    if new_user['id'] not in users_df['id'].unique(): # if its a new id
        try:
            users_df = users_df.append(new_user, ignore_index = True)
            update_users_file(users_df)

            resp = {'success': True,\
                    'message': 'החייל הוסף למערכת'}

            site_log.info(log_message(f"added user {new_user['id']} to json"))

        except Exception as e:
            print(str(e))
            resp = {'success': False,\
                    'message': str(e)}
            site_log.error(log_message(str(e)))

    else:
        resp = {'success': False,\
                'message': 'המספר האישי כבר נמצא במערכת'}
        site_log.error('tried to add a user that already exist on the db')

    return jsonify(resp)

# =========================== Remove User =============================
@app.route('/removeUser', methods=['POST']) # from mdb-editor2.js
def removeUser():
    user_id = request.form.to_dict()['id']
    try:
        users_df = cnf.USERS_DF
        users_df = users_df[users_df.id != user_id]

        update_users_file(users_df)

        resp = {'success': True,\
                'message': 'המשתמש נמחק בהצלחה'}
        site_log.info(log_message('removed user from json'))

    except Exception as e:
        print(str(e))
        resp = {'success': False,\
                'message': str(e)}
        site_log.error(log_message(str(e)))

    return jsonify(resp)

# =========================== Edit user ===============================
@app.route('/editUser', methods=['POST']) # from mdb-editor2.js
def editUser():
    form_data = request.form.to_dict()
    user = ast.literal_eval(form_data['user']) 
    exemptions = ast.literal_eval(form_data['exemptions']) 
    
    original_id = form_data['original_id']

    try:
        users_df = cnf.USERS_DF
        user_mask = users_df['id']==original_id

        user['exemptions'] = exemptions

        #update
        for column_name in set(users_df.columns):
            if column_name not in user.keys():
                new_value = users_df[user_mask][column_name]
                if len(new_value)>0:
                    new_value = new_value.values[0]
                else:
                    new_value = ""

                user[column_name] = new_value

        # delete
        users_df = users_df[users_df.id != original_id]
        # insert
        users_df = users_df.append(user, ignore_index = True)

        '''
        other mathood
        for key, value in user.items():
           users_df.loc[user_mask, key]  = value

        users_df.loc[user_mask, 'exemptions'] = str(exemptions)
        '''

        update_users_file(users_df)

        resp = {'success': True,\
                'message': 'המשתמש עודכן בהצלחה'}
        site_log.info(log_message('edited user in json'))

    except Exception as e:
        print(str(e))
        resp = {'success': False,\
                'message': str(e)}
        site_log.error(log_message(str(e)))


    site_log.info(log_message('edited user in json'))
    return jsonify(resp)

# =========================== get Exemptions =========================
@app.route('/getExemptions', methods=['POST'])
def getExemptions():
    id = request.form['id']
    users_df = cnf.USERS_DF
    user_mask = users_df['id']==id
    time.sleep(1)
    exemptions = users_df[user_mask]['exemptions']
    if len(exemptions)> 0:
        exemptions = exemptions.values[0]
        resp = {'exemptions': exemptions}
    else:
        resp = {'exemptions': {}}


    site_log.info(log_message('got ptorim'))
    return jsonify(resp)

# =========================== Give final excel ========================
@app.route('/giveExcel', methods=['POST'])
def giveExcel():

    dates = get_dates(json.loads(request.form['javascript_data']))
    toranuyot_df = pd.DataFrame({'date': map(str, dates),\
                            'day_of_week': map(str, get_day_of_week(dates)),\
                            'date_type': map(str, get_date_type(dates)),\
                            'kitchen1': '', 'kitchen2': '', 'shmirot1': '', 'shmirot2': ''})
    toranuyot_df = add_toranim(toranuyot_df) # add the toranim
    file_name = str(dates[0]) + '-' + str(dates[-1]) + '.csv'
    toranuyot_df.to_csv(file_name, index=False, header=True, encoding='utf_8-sig')
    # edit_last_json(users_df)''
    xlsx_log.info(log_message('created an excel file'))
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
