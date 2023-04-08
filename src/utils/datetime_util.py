from config_util import load_config
from datetime import datetime


def format_timestamp(timestamp):
    datetime_config = load_config()["DATETIME VALUES"]
    formatted_date = datetime.strptime(timestamp, datetime_config["DEFAULT_DATETIME_FORMAT"])
    return formatted_date
