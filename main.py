import datetime
import json
import csv
import os
import random
import re
import subprocess
import grequests
import requests
from bs4 import BeautifulSoup
from natsort import natsorted

with open("config/config.json") as config_file:
    vodrecovery_config = json.load(config_file)


def print_main_menu():
    menu = "1) Recover Vod" + "\n" + "2) Recover Clips" + "\n" + "3) Unmute an M3U8 file" + "\n" + "4) Check Segment Availability" + "\n" + "5) Generate M3U8 file (ONLY includes valid segments)" + "\n" + "6) Download M3U8 (.MP4 extension)" + "\n" + "7) Exit" + "\n"
    print(menu)


def print_vod_type_menu():
    vod_type_menu = "Enter what type of vod recovery: " + "\n" + "1) Recover Vod" + "\n" + "2) Recover vods from SullyGnome CSV export" + "\n" + "3) Exit" + "\n"
    print(vod_type_menu)


def print_vod_recovery_menu():
    vod_recovery_method = "Enter vod recovery method: " + "\n" + "1) Manual Vod Recover" + "\n" + "2) Website Vod Recover" + "\n" + "3) Exit" + "\n"
    print(vod_recovery_method)


def print_clip_type_menu():
    clip_type_menu = "Enter what type of clip recovery: " + "\n" + "1) Recover all clips from a single VOD" + "\n" + "2) Find random clips from a single VOD" + "\n" + "3) Bulk recover clips from SullyGnome CSV export" + "\n" + "4) Exit" + "\n"
    print(clip_type_menu)


def print_bulk_clip_recovery_menu():
    bulk_clip_recovery_menu = "1) Single CSV file" + "\n" + "2) Multiple CSV files" + "\n" + "3) Exit" + "\n"
    print(bulk_clip_recovery_menu)


def print_clip_recovery_menu():
    clip_recovery_method = "Enter clip recovery method: " + "\n" + "1) Manual Clip Recover" + "\n" + "2) Website Clip Recover" + "\n" + "3) Exit" + "\n"
    print(clip_recovery_method)


def print_clip_format_menu():
    clip_format_menu = "What clip url format would you like to use (delimited by spaces)? " + "\n" + "1) Default ([VodID]-offset-[interval])" + "\n" + "2) Alternate Format (vod-[VodID]-offset-[interval])" + "\n" + "3) Legacy ([VodID]-index-[interval])" + "\n"
    print(clip_format_menu)


def print_download_type_menu():
    download_type_menu = "What type of download? " + "\n" + "1) M3U8 Link" + "\n" + "2) M3U8 File" + "\n" + "3) Exit" + "\n"
    print(download_type_menu)


def get_default_directory():
    default_directory = vodrecovery_config["DIRECTORIES"]["DEFAULT_DIRECTORY"]
    return os.path.expanduser(default_directory)


def join_and_normalize_path(*file_paths):
    return os.path.normpath(os.path.join(*file_paths))


def remove_whitespace_and_lowercase(string):
    return string.strip().lower()


def get_log_filepath(streamer_name, vod_id):
    log_filename = join_and_normalize_path(get_default_directory(), f"{streamer_name}_{vod_id}_log.txt")
    return log_filename


def get_vod_filepath(streamer_name, vod_id):
    vod_filename = join_and_normalize_path(get_default_directory(), f"VodRecovery_{streamer_name}_{vod_id}.m3u8")
    return vod_filename


def generate_website_links(streamer_name, vod_id):
    website_list = [f"https://sullygnome.com/channel/{streamer_name}/stream/{vod_id}",
                    f"https://twitchtracker.com/{streamer_name}/streams/{vod_id}",
                    f"https://streamscharts.com/channels/{streamer_name}/streams/{vod_id}"]

    return website_list


def is_vod_muted(url):
    response = requests.get(url).text
    return bool("unmuted" in response)


def parse_streamer_from_m3u8_link(url):
    indices = [i.start() for i in re.finditer('_', url)]
    streamer_name = url[indices[0] + 1:indices[-2]]
    return streamer_name


def parse_vod_id_from_m3u8_link(url):
    indices = [i.start() for i in re.finditer('_', url)]
    vod_id = url[indices[0] + len(parse_streamer_from_m3u8_link(url)) + 2:indices[-1]]
    return vod_id


def parse_streamer_from_csv_filename(csv_filename):
    _, file_name = os.path.split(csv_filename)
    streamer_name = file_name.strip()
    return streamer_name.split()[0]


def parse_vod_filename(m3u8_vod_filename):
    base = os.path.basename(m3u8_vod_filename)
    streamer_name, vod_id = base.split('vodrecovery_', 1)[1].split('.m3u8', 1)[0].rsplit('_', 1)
    return f"{streamer_name}_{vod_id}"


def remove_chars_from_ordinal_numbers(datetime_string):
    datetime_config = vodrecovery_config["DATETIME VALUES"]
    for exclude_string in datetime_config["ORDINAL_NUMBERS"]:
        if exclude_string in datetime_string:
            return datetime_string.replace(datetime_string.split(" ")[1], datetime_string.split(" ")[1][:-len(exclude_string)])


def return_file_contents(streamer_name, vod_id):
    with open(get_log_filepath(streamer_name, vod_id)) as f:
        content = f.readlines()
        content = [lines.strip() for lines in content]
    return content


def parse_duration_streamscharts(tracker_url):
    for _ in range(10):
        response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
        if check_response_status_code(response):
            bs = BeautifulSoup(response.content, 'html.parser')
            streamscharts_duration = bs.find_all('div', {'class': 'text-xs font-bold'})[3].text
            if "h" in streamscharts_duration and "m" not in streamscharts_duration:
                hours = streamscharts_duration.replace("h", "")
                return get_duration(int(hours), 0)
            elif "m" in streamscharts_duration and "h" not in streamscharts_duration:
                minutes = streamscharts_duration.replace("m", "")
                return get_duration(0, int(minutes))
            else:
                split_duration = streamscharts_duration.split(" ")
                hours = split_duration[0].replace("h", "")
                minutes = split_duration[1].replace("m", "")
                return get_duration(int(hours), int(minutes))


def parse_duration_twitchtracker(tracker_url):
    response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
    if check_response_status_code(response):
        bs = BeautifulSoup(response.content, 'html.parser')
        twitchtracker_duration = bs.find_all('div', {'class': 'g-x-s-value'})[0].text
        return twitchtracker_duration


def parse_duration_sullygnome(tracker_url):
    response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
    if check_response_status_code(response):
        bs = BeautifulSoup(response.content, 'html.parser')
        sullygnome_duration = bs.find_all('div', {'class': 'MiddleSubHeaderItemValue'})[7].text.strip().replace("hours", "").replace("hour", "").replace("minutes", "").split(",")
        return get_duration(int(sullygnome_duration[0]), int(sullygnome_duration[1]))


def parse_datetime_streamscharts(tracker_url):
    for _ in range(10):
        response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
        if check_response_status_code(response):
            bs = BeautifulSoup(response.content, 'html.parser')
            streamscharts_datetime = bs.find_all('time', {'class': 'ml-2 font-bold'})[0].text.strip().replace(",", "") + ":00"
            return datetime.datetime.strftime(datetime.datetime.strptime(streamscharts_datetime, "%d %b %Y %H:%M:%S"), "%Y-%m-%d %H:%M:%S")


def parse_datetime_twitchtracker(tracker_url):
    response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
    bs = BeautifulSoup(response.content, 'html.parser')
    twitchtracker_datetime = bs.find_all('div', {'class': 'stream-timestamp-dt'})[0].text
    return twitchtracker_datetime


def parse_datetime_sullygnome(tracker_url):
    response = requests.get(tracker_url, headers=return_header(), allow_redirects=False)
    bs = BeautifulSoup(response.content, 'html.parser')
    stream_date = bs.find_all('div', {'class': 'MiddleSubHeaderItemValue'})[6].text
    modified_stream_date = remove_chars_from_ordinal_numbers(stream_date)
    formatted_stream_date = datetime.datetime.strftime(datetime.datetime.strptime(modified_stream_date, "%A %d %B %I:%M%p"), "%m-%d %H:%M:%S")
    return str(datetime.datetime.now().year) + "-" + formatted_stream_date


def unmute_vod(url):
    file_contents = []
    counter = 0
    vod_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_vod_id_from_m3u8_link(url))
    with open(vod_file_path, "w") as vod_file:
        vod_file.write(requests.get(url, stream=True).text)
    vod_file.close()
    with open(vod_file_path, "r") as vod_file:
        for lines in vod_file.readlines():
            file_contents.append(lines)
    vod_file.close()
    with open(vod_file_path, "w") as vod_file:
        for segment in file_contents:
            url = url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
            else:
                vod_file.write(segment)
    vod_file.close()
    print(join_and_normalize_path(get_default_directory(), os.path.basename(vod_file_path)) + " Has been unmuted!")


def dump_playlist(url):
    file_contents = []
    counter = 0
    vod_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_vod_id_from_m3u8_link(url))
    with open(vod_file_path, "w") as vod_file:
        vod_file.write(requests.get(url, stream=True).text)
    vod_file.close()
    with open(vod_file_path, "r") as vod_file:
        for lines in vod_file.readlines():
            file_contents.append(lines)
    vod_file.close()
    with open(vod_file_path, "w") as vod_file:
        for segment in file_contents:
            url = url.replace("index-dvr.m3u8", "")
            if not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
            else:
                vod_file.write(segment)
    vod_file.close()


def mark_invalid_segments_in_playlist(url):
    if is_vod_muted(url):
        unmute_vod(url)
    else:
        dump_playlist(url)
    modified_playlist = []
    vod_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_vod_id_from_m3u8_link(url))
    lines = open(vod_file_path, "r+").read().splitlines()
    segments = validate_playlist_segments(get_all_playlist_segments(url))
    if not segments:
        print("No segments are valid.. Cannot generate M3U8! Returning to main menu.")
        remove_file(vod_file_path)
        return
    playlist_segments = [playlist_segment for playlist_segment in segments if playlist_segment in lines]
    for segment in natsorted(playlist_segments):
        for line in lines:
            if line == segment:
                modified_playlist.append(segment)
            if line != segment and line.startswith("#"):
                modified_playlist.append(line)
            elif line.endswith(".ts") and segment not in modified_playlist and not line.startswith("#"):
                line = "#" + line
                modified_playlist.append(line)
            else:
                if line not in modified_playlist:
                    modified_playlist.append(line)
        break
    with open(vod_file_path, "w") as vod_file:
        for playlist_lines in modified_playlist:
            vod_file.write(playlist_lines + "\n")


def get_all_playlist_segments(url):
    counter = 0
    file_contents, segment_list = [], []
    vod_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_vod_id_from_m3u8_link(url))
    with open(vod_file_path, "w") as vod_file:
        vod_file.write(requests.get(url, stream=True).text)
    vod_file.close()
    with open(vod_file_path, "r") as vod_file:
        for lines in vod_file.readlines():
            file_contents.append(lines)
    vod_file.close()
    with open(vod_file_path, "w") as vod_file:
        for segment in file_contents:
            url = url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
                segment_list.append(str(url) + str(counter - 1) + "-muted.ts")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
                segment_list.append(str(url) + str(counter - 1) + ".ts")
            else:
                vod_file.write(segment)
    vod_file.close()
    return segment_list


def validate_playlist_segments(segments):
    valid_segments = []
    request_config = vodrecovery_config["REQUESTS"]
    all_segments = [url.strip() for url in segments]
    request_session = grequests.Session()
    rs = (grequests.head(u, session=request_session) for u in all_segments)
    responses = grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"])
    for i, response in enumerate(responses):
        if response is not None:
            if check_response_status_code(response):
                valid_segments.append(response.url)
        print(f"\rChecking segments.. {i + 1} / {len(all_segments)}", end="")
    segment_string = f"{len(valid_segments)} of {len(all_segments)} Segments are valid"
    print(f"\n{segment_string}" + "\n")
    return valid_segments


def vod_recover(streamer_name, vod_id, timestamp):
    vod_config = vodrecovery_config["VIDEO RECOVERY"]
    vod_age = get_vod_age(timestamp)
    if vod_age == 0:
        print("Broadcast is from today!" + "\n")
    elif vod_age > 60:
        print("Vod is older then 60 days. Chances of recovery are very slim." + "\n")
    else:
        print(f"Vod is {vod_age} day(s) old." + "\n")
    vod_url_list = get_vod_urls(streamer_name, vod_id, timestamp)
    if len(vod_url_list):
        vod_url = random.choice(vod_url_list)
        playlist_segments = get_all_playlist_segments(vod_url)
        if is_vod_muted(vod_url):
            print(vod_url)
            print("Vod contains muted segments")
            if vod_config["UNMUTE_VOD"]:
                unmute_vod(vod_url)
                if vod_config["CHECK_SEGMENTS"]:
                    validate_playlist_segments(playlist_segments)
                else:
                    user_input = input("Would you like to check if segments are valid (Y/N): ")
                    if user_input.upper() == "Y":
                        validate_playlist_segments(playlist_segments)
                    else:
                        return
            else:
                user_input = input("Would you like to unmute the vod (Y/N): ")
                if user_input.upper() == "Y":
                    unmute_vod(vod_url)
                    if vod_config["CHECK_SEGMENTS"]:
                        validate_playlist_segments(playlist_segments)
                    else:
                        user_input = input("Would you like to check if segments are valid (Y/N): ")
                        if user_input.upper() == "Y":
                            validate_playlist_segments(playlist_segments)
                        else:
                            return
                else:
                    return
        else:
            print(f"{vod_url}\nVod does NOT contain muted segments")
            if vod_config["CHECK_SEGMENTS"]:
                validate_playlist_segments(playlist_segments)
            else:
                user_input = input("Would you like to check if segments are valid (Y/N): ")
                if user_input.upper() == "Y":
                    validate_playlist_segments(playlist_segments)
                else:
                    return
            return
    else:
        print("No vods found using the current domain list.")
        for tracker_url in generate_website_links(streamer_name, vod_id):
            print(tracker_url)
        return


def manual_vod_recover():
    streamer_name = remove_whitespace_and_lowercase(input("Enter streamer name: "))
    vod_id = remove_whitespace_and_lowercase(input("Enter vod id: "))
    timestamp = remove_whitespace_and_lowercase(input("Enter VOD start time (YYYY-MM-DD HH:MM:SS): "))
    vod_recover(streamer_name, vod_id, timestamp)


def website_vod_recover():
    tracker_url = remove_whitespace_and_lowercase(input("Enter twitchtracker/streamscharts/sullygnome url:  "))
    if not tracker_url.startswith("https://"):
        tracker_url = "https://" + tracker_url
    if "streamscharts" in tracker_url:
        streamer = tracker_url.split("channels/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("streams/", 1)[1]
        vod_recover(streamer, vod_id, parse_datetime_streamscharts(tracker_url))
    elif "twitchtracker" in tracker_url:
        streamer = tracker_url.split("com/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("streams/", 1)[1]
        vod_recover(streamer, vod_id, parse_datetime_twitchtracker(tracker_url))
    elif "sullygnome" in tracker_url:
        streamer = tracker_url.split("channel/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("stream/", 1)[1]
        vod_recover(streamer, vod_id, parse_datetime_sullygnome(tracker_url))
    else:
        print("Link not supported.. Returning to main menu.")
        return


def website_clip_recover():
    tracker_url = remove_whitespace_and_lowercase(input("Enter twitchtracker/streamscharts/sullygnome url:  "))
    if not tracker_url.startswith("https://"):
        tracker_url = "https://" + tracker_url
    if "streamscharts" in tracker_url:
        streamer = tracker_url.split("channels/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("streams/", 1)[1]
        clip_recover(streamer, vod_id, parse_duration_streamscharts(tracker_url))
    elif "twitchtracker" in tracker_url:
        streamer = tracker_url.split("com/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("streams/", 1)[1]
        clip_recover(streamer, vod_id, int(parse_duration_twitchtracker(tracker_url)))
    elif "sullygnome" in tracker_url:
        streamer = tracker_url.split("channel/", 1)[1].split("/")[0]
        vod_id = tracker_url.split("stream/", 1)[1]
        clip_recover(streamer, vod_id, int(parse_duration_sullygnome(tracker_url)))
    else:
        print("Link not supported.. Returning to main menu.")
        return


def bulk_vod_recovery():
    file_path = remove_whitespace_and_lowercase(input("Enter full path of sullygnome CSV file: ").replace('"', ''))
    for timestamp, vod_id in parse_vod_csv_file(file_path).items():
        print("\n" + "Recovering Vod....", vod_id)
        vod_url_list = get_vod_urls(str(parse_streamer_from_csv_filename(file_path)).lower(), vod_id, timestamp)
        if len(vod_url_list):
            vod_url = random.choice(vod_url_list)
            if is_vod_muted(vod_url):
                print(f"{vod_url}\n Vod contains muted segments")
            else:
                print(f"{vod_url}\n Vod does NOT contain muted segments")
        else:
            print("No vods found using the current domain list.")


def clip_recover(streamer, vod_id, duration):
    total_counter, iteration_counter, valid_counter = 0, 0, 0
    valid_url_list = []
    request_config = vodrecovery_config["REQUESTS"]
    clip_config = vodrecovery_config["CLIP RECOVERY"]
    print_clip_format_menu()
    clip_format = input("Please choose an option: ").split(" ")
    full_url_list = get_all_clip_urls(get_clip_format(vod_id, get_reps(duration)), clip_format)
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in full_url_list]
    for response in grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"]):
        total_counter += 1
        iteration_counter += 1
        print('\rSearching for clips..... ' + str(iteration_counter) + " of " + str(len(full_url_list)), end=" ", flush=True)
        total_counter = 0
        if check_response_status_code(response):
            valid_counter += 1
            valid_url_list.append(response.url)
    print("\n" + str(valid_counter) + " Clip(s) Found")
    if len(valid_url_list) >= 1:
        with open(get_log_filepath(streamer, vod_id), "w") as log_file:
            for url in valid_url_list:
                log_file.write(url + "\n")
        log_file.close()
        if clip_config["DOWNLOAD_CLIPS"]:
            download_clips(get_default_directory(), streamer, vod_id)
            if clip_config["REMOVE_LOG_FILE"]:
                remove_file(get_log_filepath(streamer, vod_id))
            else:
                keep_log_option = input("Do you want to remove the log file? ")
                if keep_log_option.upper() == "Y":
                    remove_file(get_log_filepath(streamer, vod_id))
                else:
                    return
        else:
            download_option = input("Do you want to download the recovered clips (Y/N): ")
            if download_option.upper() == "Y":
                download_clips(get_default_directory(), streamer, vod_id)
                if clip_config["REMOVE_LOG_FILE"]:
                    remove_file(get_log_filepath(streamer, vod_id))
                else:
                    keep_log_option = input("Do you want to remove the log file? ")
                    if keep_log_option.upper() == "Y":
                        remove_file(get_log_filepath(streamer, vod_id))
                    else:
                        return
            else:
                remove_file(get_log_filepath(streamer, vod_id))
                return
    else:
        print("No clips found! Returning to main menu.")
        return


def manual_clip_recover():
    streamer_name = remove_whitespace_and_lowercase(input("Enter streamer name: "))
    vod_id = remove_whitespace_and_lowercase(input("Enter vod id: "))
    hours = remove_whitespace_and_lowercase(input("Enter stream duration hour value: "))
    minutes = remove_whitespace_and_lowercase(input("Enter stream duration minute value: "))
    clip_recover(streamer_name, vod_id, get_duration(hours, minutes))


def parse_clip_csv_file(file_path):
    vod_info_dict = {}
    csv_file = open(file_path, "r+")
    lines = csv_file.readlines()[1:]
    for line in lines:
        if line.strip():
            filtered_string = line.partition("stream/")[2].replace('"', "")
            modified_stream_date = remove_chars_from_ordinal_numbers(line.split(",")[1].replace('"', ""))
            stream_date = datetime.datetime.strftime(datetime.datetime.strptime(modified_stream_date, "%A %d %B %Y %H:%M"), "%d-%B-%Y")
            vod_id = filtered_string.split(",")[0]
            duration = filtered_string.split(",")[1]
            if vod_id != 0:
                reps = get_reps(int(duration))
                vod_info_dict.update({vod_id: (stream_date, reps)})
            else:
                pass
    csv_file.close()
    return vod_info_dict


def parse_vod_csv_file(file_path):
    vod_info_dict = {}
    csv_file = open(file_path, "r+")
    lines = csv_file.readlines()[1:]
    for line in lines:
        if line.strip():
            modified_stream_date = remove_chars_from_ordinal_numbers(line.split(",")[1].replace('"', ""))
            stream_date = datetime.datetime.strftime(datetime.datetime.strptime(modified_stream_date, "%A %d %B %Y %H:%M"), "%Y-%m-%d %H:%M:%S")
            vod_id = line.partition("stream/")[2].split(",")[0].replace('"', "")
            vod_info_dict.update({stream_date: vod_id})
    csv_file.close()
    return vod_info_dict


def merge_csv_files(csv_filename, path):
    csv_list = [file for file in os.listdir(path) if file.endswith(".csv")]
    header_saved = False
    with open(os.path.join(path, f"{csv_filename.title()}_MERGED.csv"), "w", newline="") as output_file:
        writer = csv.writer(output_file)
        for file in csv_list:
            with open(os.path.join(path, file), "r") as f_in:
                reader = csv.reader(f_in)
                header = next(reader)
                if not header_saved:
                    writer.writerow(header)
                    header_saved = True
                for row in reader:
                    writer.writerow(row)
    print("CSV files merged successfully!")


def random_clip_recovery():
    counter = 0
    display_limit = 5
    vod_id = remove_whitespace_and_lowercase(input("Enter vod id: "))
    hours = remove_whitespace_and_lowercase(input("Enter stream duration hour value: "))
    minutes = remove_whitespace_and_lowercase(input("Enter stream duration minute value: "))
    request_config = vodrecovery_config["REQUESTS"]
    print_clip_format_menu()
    clip_format = input("Please choose an option: ").split(" ")
    full_url_list = get_all_clip_urls(get_clip_format(vod_id, get_reps(get_duration(hours, minutes))), clip_format)
    random.shuffle(full_url_list)
    print("Total Number of Urls: " + str(len(full_url_list)))
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in full_url_list]
    for response in grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"]):
        if check_response_status_code(response):
            counter += 1
            if counter <= display_limit:
                print(response.url)
            if counter == display_limit:
                user_option = input("Do you want to see more urls (Y/N): ")
                if user_option.upper() == "Y":
                    display_limit = min(display_limit + 3, len(full_url_list))
                else:
                    break
    return


def bulk_clip_recovery():
    vod_counter, total_counter, valid_counter, iteration_counter = 0, 0, 0, 0
    streamer_name, csv_file_path = "", ""
    request_config = vodrecovery_config["REQUESTS"]
    print_bulk_clip_recovery_menu()
    bulk_recovery_option = input("Please choose an option: ")
    if bulk_recovery_option == "1":
        csv_file_path = remove_whitespace_and_lowercase(input("Enter full path of sullygnome CSV file: ").replace('"', ''))
        streamer_name = parse_streamer_from_csv_filename(csv_file_path)
    elif bulk_recovery_option == "2":
        csv_directory = remove_whitespace_and_lowercase(input("Enter the full path where the sullygnome csv files exist: ").replace('"', ''))
        streamer_name = input("Enter the streamer's name: ")
        merge_files = input("Do you want to merge the CSV files in the directory? (Y/N): ")
        if merge_files.upper() == "Y":
            merge_csv_files(streamer_name, csv_directory)
            csv_file_path = join_and_normalize_path(csv_directory, f"{streamer_name.title()}_MERGED.csv")
        else:
            csv_file_path = input("Enter full path of sullygnome CSV file: ")
            csv_file_path = remove_whitespace_and_lowercase(csv_file_path.replace('"', ''))
            streamer_name = parse_streamer_from_csv_filename(csv_file_path)
    elif bulk_recovery_option == "3":
        exit()
    user_option = input("Do you want to download all clips recovered (Y/N)? ")
    print_clip_format_menu()
    clip_format = input("Please choose an option: ").split(" ")
    for vod_id, values in parse_clip_csv_file(csv_file_path).items():
        vod_counter += 1
        print("\nProcessing Past Broadcast: \n"
              + "Stream Date: " + values[0].replace("-", " ") + "\n"
              + "Vod ID: " + str(vod_id) + "\n"
              + "Vod Number: " + str(vod_counter) + " of " + str(len(parse_clip_csv_file(csv_file_path))) + "\n")
        original_vod_url_list = get_all_clip_urls(get_clip_format(vod_id, values[1]), clip_format)
        request_session = requests.Session()
        rs = [grequests.head(u, session=request_session) for u in original_vod_url_list]
        for response in grequests.imap(rs, size=request_config["MAX_REQUEST_SIZE"]):
            total_counter += 1
            iteration_counter += 1
            print('\rSearching for clips..... ' + str(iteration_counter) + " of " + str(len(original_vod_url_list)), end=" ", flush=True)
            total_counter = 0
            if check_response_status_code(response):
                valid_counter += 1
                with open(get_log_filepath(streamer_name, vod_id), "a+") as log_file:
                    log_file.write(response.url + "\n")
                log_file.close()
            else:
                continue
        print('\n' + str(valid_counter) + " Clip(s) Found")
        if valid_counter != 0:
            if user_option.upper() == "Y":
                download_clips(get_default_directory(), streamer_name, vod_id)
                remove_file(get_log_filepath(streamer_name, vod_id))
            else:
                print("Recovered clips logged to " + get_log_filepath(streamer_name, vod_id))
        else:
            print("No clips found!... Moving on to next vod." + "\n")
        total_counter, valid_counter, iteration_counter = 0, 0, 0


def download_m3u8_video_url(url, file_name):
    ffmpeg_commands = vodrecovery_config["FFMPEG"]
    command = ffmpeg_commands["DOWNLOAD_M3U8_VIDEO_URL"].format(url, join_and_normalize_path(get_default_directory(), file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_url_slice(url, file_name, start_time, end_time):
    ffmpeg_commands = vodrecovery_config["FFMPEG"]
    command = ffmpeg_commands["DOWNLOAD_M3U8_VIDEO_URL_SLICE"].format(start_time, end_time, url, join_and_normalize_path(get_default_directory(), file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_file(m3u8_file_path, file_name):
    ffmpeg_commands = vodrecovery_config["FFMPEG"]
    command = ffmpeg_commands["DOWNLOAD_M3U8_VIDEO_FILE"].format(m3u8_file_path, join_and_normalize_path(get_default_directory(), file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_file_slice(m3u8_file_path, file_name, start_time, end_time):
    ffmpeg_commands = vodrecovery_config["FFMPEG"]
    command = ffmpeg_commands["DOWNLOAD_M3U8_VIDEO_FILE_SLICE"].format(start_time, end_time, m3u8_file_path, join_and_normalize_path(get_default_directory(), file_name))
    subprocess.call(command, shell=True)


def download_clips(directory, streamer_name, vod_id):
    counter = 0
    print("Starting Download....")
    download_directory = join_and_normalize_path(directory, streamer_name.title() + "_" + vod_id)
    if os.path.exists(download_directory):
        pass
    else:
        os.mkdir(download_directory)
    for links in return_file_contents(streamer_name, vod_id):
        counter = counter + 1
        link_url = os.path.basename(links)
        response = requests.get(links, stream=True)
        if str(link_url).endswith(".mp4"):
            with open(join_and_normalize_path(download_directory, streamer_name.title() + "_" + str(vod_id) + "_" + str(
                    extract_offset(links))) + ".mp4", 'wb') as x:
                print("Downloading Clip... " + str(
                    counter) + " of " + str(len(return_file_contents(streamer_name, vod_id))) + " - " + links)
                x.write(response.content)
        else:
            print("ERROR: Please check the log file and failing link!", links)


def run_script():
    print("WELCOME TO VOD RECOVERY" + "\n")
    menu = 0
    while menu < 7:
        print_main_menu()
        menu = int(input("Please choose an option: "))
        if menu == 7:
            exit()
        elif menu == 1:
            print_vod_type_menu()
            vod_type = int(input("Please choose an option: "))
            if vod_type == 1:
                print_vod_recovery_menu()
                vod_recovery_method = int(input("Please choose an option: "))
                if vod_recovery_method == 1:
                    manual_vod_recover()
                elif vod_recovery_method == 2:
                    website_vod_recover()
                elif vod_recovery_method == 3:
                    exit()
                else:
                    print("Invalid option returning to main menu.")
            elif vod_type == 2:
                bulk_vod_recovery()
            elif vod_type == 3:
                exit()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 2:
            print_clip_type_menu()
            clip_type = int(input("Please choose an option: "))
            if clip_type == 1:
                print_clip_recovery_menu()
                clip_recovery_method = int(input("Please choose an option: "))
                if clip_recovery_method == 1:
                    manual_clip_recover()
                elif clip_recovery_method == 2:
                    website_clip_recover()
                elif clip_recovery_method == 3:
                    exit()
                else:
                    print("Invalid option returning to main menu.")
            elif clip_type == 2:
                random_clip_recovery()
            elif clip_type == 3:
                bulk_clip_recovery()
            elif clip_type == 4:
                exit()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 3:
            url = remove_whitespace_and_lowercase(input("Enter M3U8 Link: "))
            if is_vod_muted(url):
                unmute_vod(url)
            else:
                print("Vod does NOT contain muted segments")
        elif menu == 4:
            url = remove_whitespace_and_lowercase(input("Enter M3U8 Link: "))
            validate_playlist_segments(get_all_playlist_segments(url))
            remove_file(get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_vod_id_from_m3u8_link(url)))
        elif menu == 5:
            url = remove_whitespace_and_lowercase(input("Enter M3U8 Link: "))
            mark_invalid_segments_in_playlist(url)
        elif menu == 6:
            print_download_type_menu()
            download_type = int(input("Please choose an option: "))
            if download_type == 1:
                vod_url = remove_whitespace_and_lowercase(input("Enter M3U8 Link: "))
                vod_filename = "{}_{}.mp4".format(parse_streamer_from_m3u8_link(vod_url), parse_vod_id_from_m3u8_link(vod_url))
                trim_vod = input("Would you like to specify the start and end time of the vod (Y/N)? ")
                if trim_vod.upper() == "Y":
                    vod_start_time = input("Enter start time (HH:MM:SS): ")
                    vod_end_time = input("Enter end time (HH:MM:SS): ")
                    download_m3u8_video_url_slice(vod_url, vod_filename, vod_start_time, vod_end_time)
                    print("Vod downloaded to {}".format(join_and_normalize_path(get_default_directory(), vod_filename)))
                else:
                    download_m3u8_video_url(vod_url, vod_filename)
                    print("Vod downloaded to {}".format(join_and_normalize_path(get_default_directory(), vod_filename)))
            elif download_type == 2:
                m3u8_file_path = remove_whitespace_and_lowercase(input("Enter absolute file path of the M3U8: "))
                trim_vod = input("Would you like to specify the start and end time of the vod (Y/N)? ")
                if trim_vod.upper() == "Y":
                    vod_start_time = input("Enter start time (HH:MM:SS): ")
                    vod_end_time = input("Enter end time (HH:MM:SS): ")
                    download_m3u8_video_file_slice(m3u8_file_path, parse_vod_filename(m3u8_file_path) + ".mp4", vod_start_time, vod_end_time)
                    print("Vod downloaded to {}".format(join_and_normalize_path(get_default_directory(), parse_vod_filename(m3u8_file_path) + ".mp4")))
                else:
                    download_m3u8_video_file(m3u8_file_path, parse_vod_filename(m3u8_file_path) + ".mp4")
                    print("Vod downloaded to {}".format(join_and_normalize_path(get_default_directory(), parse_vod_filename(m3u8_file_path) + ".mp4")))
            elif download_type == 3:
                exit()
        else:
            print("Invalid Option! Exiting...")


if __name__ == '__main__':
    run_script()
