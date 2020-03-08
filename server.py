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
    usersFile = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))

    site_log.info(log_message('got users'))
    return render_template('index.html', users=usersFile)

# =========================== Add User ================================
@app.route('/addUser', methods=['POST'])  # from mdb-editor2.js
def addUser():
    jsdata = request.form['javascript_data']
    new_user = jsdata.split(',')
    user = {"id": str(new_user[0]), "name": new_user[1], "unit": new_user[2], "last_toranut": '2000-01-01',
            "last_weekend": '2000-01-01', "ptorim": {'פטור שמירות אמצ"ש': new_user[3], 'פטור שמירות סופ"ש': new_user[4],
                                                     'פטור מטבחים אמצ"ש': new_user[5], 'פטור מטבחים סופ"ש': new_user[6]}}
    new_data = json.load(codecs.open(users_file, 'r', 'utf-8-sig'))
    new_data.append(user)
    writes_to_json(new_data, users_file)

    site_log.info(log_message('added user to json'))
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

    site_log.info(log_message('removed user from json'))
    return '', 204

# =========================== Edit user ===============================
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
    first_time = time.time()

    dates = get_dates(json.loads(request.form['javascript_data']))
    final_csv = pd.DataFrame({'date': map(str, dates),\
                            'day_of_week': map(str, get_day_of_week(dates)),\
                            'date_type': map(str, get_date_type(dates)),\
                            'kitchen1': '', 'kitchen2': '', 'shmirot1': '', 'shmirot2': ''})
    final_csv = add_toranim(final_csv)
    file_name = str(dates[0]) + '-' + str(dates[-1]) + '.csv'
    final_csv.to_csv(file_name, index=False, header=True, encoding='utf_8-sig')
    # edit_last_json(users_df)''
    xlsx_log.info(log_message('created an excel file'))
    print(f'it took {time.time()-first_time} seconds')
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
