import pandas as pd

EXEMPTS_WEEKDAY = {
    'kitchen1': "פטור מטבחים אמצש",
    'kitchen2': "פטור מטבחים אמצש",
    'shmirot1': "פטור שמירות אמצש",
    'shmirot2': "פטור שמירות אמצש"
}

EXEMPTS_WEEKEND = {
    'kitchen1': "פטור מטבחים סופש",
    'kitchen2': "פטור מטבחים סופש",
    'shmirot1': "פטור שמירות סופש",
    'shmirot2': "פטור שמירות סופש"
}

MIN_DAYS_BETWEEN_WEEKDAY_TORANUTS = 2
MIN_DAYS_BETWEEN_WEEKEND_TORANUTS = 4
