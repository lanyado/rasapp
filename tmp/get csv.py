import pandas as pd
import json
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
users_file = os.path.join(current_dir, 'db/users.json')
soldiers_df = pd.read_json('db/users.json', encoding='utf-8-sig')
soldiers_df.to_csv('db.csv', index=False, header=True, encoding='utf_8-sig')
