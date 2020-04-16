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
from get_toranim import add_toranim

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import pandas as pd
#import modin.pandas as pd

import ast

from functools import wraps

app = Flask(__name__, template_folder=os.path.join(cnf.CURRENT_DIR, 'static'))  # Runs the HTML from the static folder

site_log = get_log('Website')
xlsx_log = get_log('XLSX')

loged_in = False

def checkUser(func):
    """Checks whether user is logged in or send him to the login page"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not loged_in:
            return render_template('login.html')
        return func(*args, **kwargs)
    return wrapper

def remove_exemptions(exemptions):
    new_exemptions = {}
    if len(exemptions)>0:
        for name, date in exemptions.items():
            if datetime.strptime(date,'%Y-%m-%d') >= datetime.today():
                new_exemptions[name] = date
    return new_exemptions

def remove_expired_exemptions():
    users_df = cnf.get_users_df()
    users_df['exemptions'] = users_df['exemptions'].apply(remove_exemptions)
    cnf.update_users_file(users_df)

def get_toranuyot_table_names():
    filenames = glob.glob('results/*') # * means all if need specific format then *.csv
    filenames.sort(key=os.path.getctime)

    latest_file = max(filenames, key=os.path.getctime)
    
    filenames[filenames.index(latest_file)] = f'{latest_file} הכי חדש'

    filenames = [file_name.split('/')[1] for file_name in filenames]
    return filenames

# =========================== login finction ============================

@app.route('/login', methods = ['POST'])
def login():
    password = request.form.to_dict()['password']
    if password == ' ':
        global loged_in
        loged_in = True
        resp = {'auth': True,\
                'redirect_url':url_for('dashboard')}
    else:
        resp = {'auth':False}

    return jsonify(resp)

# =========================== landing page rander ============================
@app.route("/")  # Opens index.html when the user searches for http://127.0.0.1:5000/
@checkUser
def dashboard():
    remove_expired_exemptions()
    users = json.load(codecs.open(cnf.USERS_JSON_FILE, 'r', 'utf-8-sig'))

    toranuyot_tables = get_toranuyot_table_names()

    site_log.info(log_message('got users'))
    return render_template('dashboard.html', users=users, toranuyot_tables=toranuyot_tables)

# =========================== Add User ================================
@app.route('/addUser', methods=['POST'])
@checkUser
def addUser():
    new_user = request.form.to_dict()
    new_user['exemptions'] = ast.literal_eval(new_user['exemptions'])

    users_df = cnf.get_users_df()

    if new_user['id'] not in users_df['id'].unique(): # if its a new id
        try:
            users_df = users_df.append(new_user, ignore_index = True)
            cnf.update_users_file(users_df)

        except Exception as e:
            print(str(e))
            resp = {'success': False,\
                    'message': str(e)}
            site_log.error(log_message(str(e)))

        else:
            resp = {'success': True,\
                    'message': 'החייל הוסף למערכת'}
            site_log.info(log_message(f"added user {new_user['id']} to json"))

    else:
        resp = {'success': False,\
                'message': 'המספר האישי כבר נמצא במערכת'}
        site_log.error('tried to add a user that already exist on the db')

    return jsonify(resp)

# =========================== Remove User =============================
@app.route('/removeUser', methods=['POST']) # from mdb-editor2.js
@checkUser
def removeUser():
    user_id = request.form.to_dict()['id']
    try:
        users_df = cnf.get_users_df()
        users_df = users_df[users_df.id != user_id]

        cnf.update_users_file(users_df)

    except Exception as e:
        print(str(e))
        resp = {'success': False,\
                'message': str(e)}
        site_log.error(log_message(str(e)))

    else:
        resp = {'success': True,\
                'message': 'המשתמש נמחק בהצלחה'}
        site_log.info(log_message('removed user from json'))

    return jsonify(resp)

# =========================== Edit user ===============================
@app.route('/editUser', methods=['POST']) # from mdb-editor2.js
@checkUser
def editUser():
    form_data = request.form.to_dict()
    user = ast.literal_eval(form_data['user'])
    exemptions = ast.literal_eval(form_data['exemptions'])
    original_id = form_data['original_id']

    user['exemptions'] = exemptions
    try:
        users_df = cnf.get_users_df()
        user_mask = users_df['id'] == original_id

        #update the user with keys it hasn't have
        for column_name in set(users_df.columns):
            if column_name not in user.keys():
                new_value = users_df[user_mask][column_name]
                if len(new_value)>0:
                    new_value = new_value.values[0]
                else:
                    new_value = ""
                user[column_name] = new_value

        # delete from users_df
        users_df = users_df[users_df.id != original_id]
        # insert to users_df
        users_df = users_df.append(user, ignore_index = True)

        cnf.update_users_file(users_df)

    except Exception as e:
        print(str(e))
        resp = {'success': False,\
                'message': str(e)}
        site_log.error(log_message(str(e)))

    else:
        resp = {'success': True,\
                'message': 'המשתמש עודכן בהצלחה'}
        site_log.info(log_message('edited user in json'))

    finally:
        return jsonify(resp)

# =========================== get Exemptions =========================
@app.route('/getExemptions', methods=['POST'])
@checkUser
def getExemptions():
    id = request.form['id']
    users_df = cnf.get_users_df()
    user_mask = users_df['id']==id
    exemptions = users_df[user_mask]['exemptions']
    if len(exemptions)> 0:
        exemptions = exemptions.values[0]
        resp = {'exemptions': exemptions}
    else:
        resp = {'exemptions': {}}

    site_log.info(log_message('got ptorim'))
    return jsonify(resp)

# =========================== Give final excel ========================
@app.route('/getToranim', methods=['POST'])
@checkUser
def getToranim():
    form_data = request.form.to_dict()
    dates = get_dates(ast.literal_eval(form_data['dates']))

    toranuyot_df = pd.DataFrame({'date': map(str, dates),\
                                 'day_of_week': map(str, get_day_of_week(dates)),\
                                 'date_type': map(str, get_date_type(dates)),\
                                 'kitchen1': '', 'kitchen2': '', 'shmirot1': '', 'shmirot2': ''})
    try:
        toranuyot_df = add_toranim(toranuyot_df) # add the toranim
    except Exception as e:
        error_message = getattr(e, 'message', str(e))
        print(error_message)
        if error_message == 'no available toranim':
            resp = {'success': False,\
                    'message': 'אין מספיק תורנים'}
            xlsx_log.error(log_message(str(e)))
    else:
        resp = {'success': True,\
                'message': 'חלוקת התורנים התבצעה בהצלחה',\
                'redirect_url':url_for('last_toranuyot_table')}

        toranuyot_df.rename(inplace = True,\
                            columns={'date': 'תאריך',\
                                     'day_of_week': 'יום בשבוע',\
                                     'date_type': 'סוג תאריך',\
                                     'kitchen1': 'תורן מטבח 1', 'kitchen2': 'תורן מטבח 2', 'shmirot1': 'תורן שמירות 1', 'shmirot2': 'תורן שמירות 2'})

        file_name = f'{dates[0]}_{dates[-1]}.csv'

        toranuyot_df.to_csv(f'results/{file_name}', index=False, header=True, encoding='utf-8-sig')
        xlsx_log.info(log_message('created an excel file'))

    finally:
        return jsonify(resp)
# =========================== toranuyot table rander ============================

@app.route("/toranuyot-table", methods=['GET'])
@checkUser
def last_toranuyot_table():
    filename = request.args.get('filename', None)
    df = pd.read_csv('results/'+filename)
    return render_template('toranuyot-table.html', table = df.to_html(), min_date = min(df['תאריך']), max_date = max(df['תאריך']))

if __name__ == "__main__":
    app.run(debug=True)
