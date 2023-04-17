from config_util import load_config
from datetime import datetime
from datetime import timedelta


def format_timestamp(timestamp):
    datetime_config = load_config()["DATETIME VALUES"]
    formatted_date = datetime.strptime(timestamp, datetime_config["DEFAULT_DATETIME_FORMAT"])
    return formatted_date


def compute_epoch_timestamp(timestamp, seconds):
    # Calculate epoch_timestamp based on the timestamp/seconds parameters
    epoch_timestamp = (format_timestamp(timestamp) + timedelta(seconds=seconds) - datetime(1970, 1, 1)).total_seconds()
    # Return the epoch_timestamp
    return epoch_timestamp


def compute_timestamp_difference_in_days(start_timestamp, end_timestamp):
    # Using the broadcasts start and end times calculate the time difference
    start_date = format_timestamp(start_timestamp)
    end_date = format_timestamp(end_timestamp)
    difference = end_date - start_date
    # Return the time difference in days
    return max(difference.days, 0)
