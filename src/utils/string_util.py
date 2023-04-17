from config_util import load_config


def remove_chars_from_ordinal_numbers(datetime_string):
    date_config = load_config()
    datetime_config = date_config["DATETIME VALUES"]
    for exclude_string in datetime_config["ORDINAL_NUMBERS"]:
        if exclude_string in datetime_string:
            return datetime_string.replace(datetime_string.split(" ")[1], datetime_string.split(" ")[1][:-len(exclude_string)])
