import hashlib
import grequests
import requests
from datetime_util import compute_epoch_timestamp
from config_util import load_config
import web_util


def compute_vod_duration_in_minutes(hours, minutes):
    # Calculate and return the vod duration in minutes
    return (int(hours) * 60) + int(minutes)


def return_qualities():
    qualities = [
        "chunked",
        "1080p60",
        "1080p30",
        "1080p60fps",
        "1080p30",
        "1080p60",
        "1080p30",
        "1080p60",
        "1080p30",
        "936p60",
        "936p30",
        "900p60",
        "900p30",
        "720p60",
        "720p30",
        "480p60",
        "480p30",
        "360p60",
        "360p30",
        "160p60",
        "160p30",
        "144p60",
        "144p30",
        "audio_only"
    ]
    return qualities


def get_vod_urls(streamer, vod_id, timestamp):
    vod_url_list, valid_vod_url_list = [], []
    request_config = load_config()["REQUESTS"]
    qualities = return_qualities()
    added_qualities = set()
    # Loop through each second in 1 minute
    for seconds in range(59):
        # Construct the base url given the parameters and use the compute_epoch_timestamp to calculate the epoch timestamp
        base_url = streamer + "_" + vod_id + "_" + str(int(compute_epoch_timestamp(timestamp, seconds)))
        # Get the first 20 characters of the SHA1
        hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
        for domain in web_util.return_domain_list():
            for quality in qualities:
                if quality in added_qualities:
                    continue
                # Using the domain list, 20 character hash, base url, and quality, construct the m3u8 link
                vod_url_list.append(f"{domain}{hashed_base_url}_{base_url}/{quality}/index-dvr.m3u8")
                added_qualities.add(quality)  # Update the set
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in vod_url_list]
    # Using grequests make a get request to each url and add the successful ones to a list
    for response in grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"]):
        if web_util.check_response_status_code(response):
            valid_vod_url_list.append(response.url)
    valid_urls_set = set(valid_vod_url_list)
    valid_vod_url_list = list(valid_urls_set)
    # Return the list
    return valid_vod_url_list
