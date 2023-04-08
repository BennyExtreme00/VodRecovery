from config_util import load_config
from datetime import datetime


def format_timestamp(timestamp):
    datetime_config = load_config()["DATETIME VALUES"]
    formatted_date = datetime.strptime(timestamp, datetime_config["DEFAULT_DATETIME_FORMAT"])
    return formatted_date


def compute_timestamp_difference_in_days(start_timestamp, end_timestamp):
    start_date = format_timestamp(start_timestamp)
    end_date = format_timestamp(end_timestamp)
    difference = end_date - start_date
    return max(difference.days, 0)
