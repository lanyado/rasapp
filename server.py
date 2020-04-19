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
from lib.helpers import remove_expired_exemptions, get_duty_table_names, new_user_hundle

from get_workers import add_workers

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, get_template_attribute
import pandas as pd
#import modin.pandas as pd

import ast

from functools import wraps

app = Flask(__name__, template_folder=os.path.join(cnf.CURRENT_DIR, 'static'))  # Runs the HTML from the static folder

site_log = get_log('Website')
xlsx_log = get_log('XLSX')

loged_in = False

def checkUser (func):
    """Checks whether user is logged in or send him to the login page"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not loged_in:
            return render_template('login.html')
        return func(*args, **kwargs)
    return wrapper

# =========================== login function ============================
@app.route('/login', methods = ['POST'])
def login():
    password = request.form.to_dict()['password']
    if password == ' ':
        global loged_in
        loged_in = True
        resp = {'auth': True,\
                'redirect_url': url_for('dashboard')}
    else:
        resp = {'auth':False}

    return jsonify(resp)

# =========================== landing page rander ============================
@app.route("/")  # Opens index.html when the user searches for http://127.0.0.1:5000/
@checkUser
def dashboard ():
    # preperations before rendering the page
    remove_expired_exemptions()

    users = json.load(codecs.open(cnf.USERS_JSON_FILE, 'r', 'utf-8-sig'))
    duty_tables = get_duty_table_names()

    site_log.info(log_message('randering dashboard'))
    return render_template('dashboard.html', users=users, duty_tables=duty_tables)

# =========================== Add User ================================


@app.route('/addUser', methods=['POST'])
@checkUser
def addUser():
    new_user = request.form.to_dict()
    new_user['exemptions'] = ast.literal_eval(new_user['exemptions'])
    new_user = new_user_hundle(new_user)
    
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
def removeUser ():
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

    finally:
        return jsonify(resp)

# =========================== Edit user ===============================
@app.route('/editUser', methods=['POST']) # from mdb-editor2.js
@checkUser
def editUser ():
    form_data = request.form.to_dict()
    user = ast.literal_eval(form_data['user'])
    exemptions = ast.literal_eval(form_data['exemptions'])
    user['exemptions'] = exemptions

    original_id = form_data['original_id']
    
    try:
        users_df = cnf.get_users_df()
        user_mask = users_df['id'] == original_id

        # update the user with keys it hasn't have
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
def getExemptions ():
    id = request.form['id']
    users_df = cnf.get_users_df()
    user_mask = users_df['id']==id
    exemptions = users_df[user_mask]['exemptions'].values[0]
    
    resp = {'exemptions': exemptions}
   
    site_log.info(log_message('got exemptions'))
    return jsonify(resp)

# =========================== Give final excel ========================
@app.route('/getWorkers', methods=['POST'])
@checkUser
def getWorkers ():
    form_data = request.form.to_dict()
    dates = get_dates(ast.literal_eval(form_data['dates']))

    duties_df = pd.DataFrame({'date': map(str, dates),\
                                 'day_of_week': map(str, get_day_of_week(dates)),\
                                 'date_type': map(str, get_date_type(dates)),\
                                 'kitchen1': '', 'kitchen2': '', 'shmirot1': '', 'shmirot2': ''})
    try:
        duties_df = add_workers(duties_df) # add the workers
    except Exception as e:
        error_message = getattr(e, 'message', str(e))
        print(error_message)
        if error_message == 'No available workers':
            resp = {'success': False,\
                    'message': 'אין מספיק תורנים'}
            xlsx_log.error(log_message(str(e)))
    else:
        duties_df.rename(inplace = True,\
                            columns={'date': 'תאריך',\
                                     'day_of_week': 'יום בשבוע',\
                                     'date_type': 'סוג תאריך',\
                                     'kitchen1': 'תורן מטבח 1', 'kitchen2': 'תורן מטבח 2', 'shmirot1': 'תורן שמירות 1', 'shmirot2': 'תורן שמירות 2'})

        file_name = f'{dates[0]}_{dates[-1]}.csv'

        duties_df.to_csv(f'results/{file_name}', index=False, header=True, encoding='utf-8-sig')
        xlsx_log.info(log_message('created an excel file'))

        resp = {'success': True,\
                'message': 'חלוקת התורנים התבצעה בהצלחה',\
                'filename':file_name}

    finally:
        return jsonify(resp)

# =========================== duties table ============================
@app.route("/duties-table", methods=['GET'])
@checkUser
def open_duties_table ():
    filename = request.args.get('filename', None)
    df = pd.read_csv('results/'+filename)
    return render_template('duties-table.html', table = df.to_html(), min_date = min(df['תאריך']), max_date = max(df['תאריך']))

if __name__ == "__main__":
    app.run(debug=True)