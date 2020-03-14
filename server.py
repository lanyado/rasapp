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
#import modin.pandas as pd
#from typing import Any

current_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder=os.path.join(current_dir, 'static'))  # Runs the HTML from the static folder
users_file = os.path.join(current_dir, 'db/users.json')
#exemptions_file = os.path.join(current_dir, 'db/exemptions.csv')

site_log = get_log('Website')
xlsx_log = get_log('XLSX')

def writes_to_json(data_written, edited_file):
    """Takes data to write and puts it in the file"""
    with open(edited_file, "w", encoding='utf-8') as json_file:
        json.dump(data_written, json_file, ensure_ascii=False, indent=1)

def edit_last_json(csv):
    final_users = csv.to_dict('index')
    f2 = []
    for key in final_users:
        f2.append(final_users[key])
    writes_to_json(f2, 'db/users.json')

# =========================== landing page rander ============================
@app.route("/")  # Opens index.html when the user searches for http://127.0.0.1:5000/
def hello():
    #users_df = pd.read_json(users_file)
    #exemptions_df = pd.read_csv(exemptions_file)
    users = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))

    site_log.info(log_message('got users'))
    return render_template('index.html', users=users)

# =========================== Add User ================================
@app.route('/addUser', methods=['POST'])  # from mdb-editor2.js
def addUser():

    new_user = request.form.to_dict()
    print(f'============== {new_user}') # -> NONE

    new_user = {k: v for k, v in new_user.items()}

    print(f'============== {new_user}')  # -> NONE

    users_df = pd.read_json(users_file)
    if new_user['id'] not in users_df['id']: # if its a new id
        try:
            users_df.append(new_user)
            users_df.to_json(users_file)
            resp = {'add_successful': True,\
                    'message': 'החייל הוסף למערכת'}

        except Exception:
            resp = {'add_successful': False,\
                    'message': str(Exception)}
    else:
        resp = {'add_successful': False,\
                'message': 'המספר האישי כבר נמצא במערכת'}

    return jsonify(resp)

    '''
    new_data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data.append(user)
    writes_to_json(new_data, users_file)
    '''
    site_log.info(log_message('added user to json'))
    #return '', 204

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

    site_log.info(log_message('removed user from json'))
    return '', 204

# =========================== Edit user ===============================
@app.route('/editUser', methods=['POST']) # from mdb-editor2.js
def editUser():
    user_fields = request.form.to_dict()
    user_fields = {k: v for k, v in user_fields.items() if v}

    data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data = []
    for line in data:
        if line['id'] != user_fields['original_id']:
            new_data.append(line)
        else:
            user["last_toranut"] = line["last_toranut"]
            user["last_weekend"] = line["last_toranut"]
            new_data.append(user)

    writes_to_json(new_data, users_file)

    site_log.info(log_message('updated user in json'))
    return '', 204

# =========================== get Exemptions =========================
@app.route('/getPtorim', methods=['POST'])
def getPtorim():
    id = request.form['javascript_data']
    data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    for line in data:
        if line['id'] == id:
            site_log.info(log_message('got ptorim'))
            return jsonify({'ptorim': line['ptorim']})
            # return dict(line['ptorim'])

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
