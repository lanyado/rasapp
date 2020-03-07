# coding=utf-8
import datetime
import pandas as pd
#import modin.pandas as pd

def get_dates(dates):
    dates_list = []
    for year in dates:
        y = year
        for month in dates[year]:
            m = month
            for day in dates[year][month]:
                d = day
                dates_list.append(datetime.date(int(y), int(m) + 1, int(d)))
    return dates_list

def get_day_of_week(days_checked):
    days_list = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
    day_of_week_list = []
    for day in days_checked:
        day_of_week_list.append(days_list[day.weekday()])
    return day_of_week_list

def get_date_type(dates_list):
    holidays = pd.read_csv('db/holidays.csv', dtype={'Nmae':'str', 'Date':'str'})
    dates_type = []
    for date in dates_list:
        if str(date) in holidays.Date.values:
            dates_type.append('holiday: ' + holidays[holidays['Date'] == str(date)]['Name'].iloc[0])
        else:
            dates_type.append('סופש' if date.weekday() in [3, 4, 5] else 'אמצע שבוע')
    return dates_type
