import pandas as pd

EXEMPTS_WEEKDAY = {
    'kitchen1': "פטור מטבחים אמצ\"ש",
    'kitchen2': "פטור מטבחים אמצ\"ש",
    'shmirot1': "פטור שמירות אמצ\"ש",
    'shmirot2': "פטור שמירות אמצ\"ש"
}
EXEMPTS_WEEKEND = {
    'kitchen1': "פטור מטבחים סופ\"ש",
    'kitchen2': "פטור מטבחים סופ\"ש",
    'shmirot1': "פטור שמירות סופ\"ש",
    'shmirot2': "פטור שמירות סופ\"ש"
}

MIN_DAYS_BETWEEN_WEEKDAY_TORANUTS = 2
MIN_DAYS_BETWEEN_WEEKEND_TORANUTS = 4
