import datetime
import hashlib

from datetime import timedelta
import grequests
import requests

from config_util import load_config
from datetime_util import format_timestamp
import web_util


def compute_vod_duration_in_minutes(hours, minutes):
    # Calculate and return the vod duration in minutes
    return (int(hours) * 60) + int(minutes)


def get_vod_urls(streamer, vod_id, timestamp):
    vod_url_list, valid_vod_url_list = [], []
    request_config = load_config()["REQUESTS"]
    for seconds in range(60):
        epoch_timestamp = (format_timestamp(timestamp) + timedelta(seconds=seconds) - datetime.datetime(1970, 1, 1)).total_seconds()
        base_url = streamer + "_" + vod_id + "_" + str(int(epoch_timestamp))
        hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
        for domain in web_util.return_domain_list():
            vod_url_list.append(f"{domain}{hashed_base_url}_{base_url}/chunked/index-dvr.m3u8")
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in vod_url_list]
    for response in grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"]):
        if web_util.check_response_status_code(response):
            print(response, response.url)
            valid_vod_url_list.append(response.url)
    return valid_vod_url_list


print((get_vod_urls("amouranth", "48269475405", "2023-04-07 03:33:00")))
