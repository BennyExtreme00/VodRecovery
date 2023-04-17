import csv
from datetime import datetime
from clip_util import compute_clip_range
from string_util import remove_chars_from_ordinal_numbers


def parse_clips_csv(file_path):
    vod_info_dict = {}
    with open(file_path, "r+") as clips_csv:
        reader = csv.reader(clips_csv)
        next(reader)
        for row in reader:
            stream_date = datetime.strftime(datetime.strptime(remove_chars_from_ordinal_numbers(row[1].replace('"', "")), "%A %d %B %Y %H:%M"), "%d-%B-%Y")
            vod_id = row[2].partition("stream/")[2]
            duration = row[3]
            if vod_id != 0:
                clip_range = compute_clip_range(int(duration))
                vod_info_dict.update({vod_id: (stream_date, clip_range)})
        return vod_info_dict


def parse_vod_csv(file_path):
    vod_info_dict = {}
    with open(file_path, "r+") as vods_csv:
        reader = csv.reader(vods_csv)
        next(reader)
        for row in reader:
            stream_date = datetime.strftime(datetime.strptime(remove_chars_from_ordinal_numbers(row[1].replace('"', "")), "%A %d %B %Y %H:%M"), "%d-%B-%Y")
            vod_id = row[2].partition("stream/")[2]
            if vod_id != 0:
                vod_info_dict.update({stream_date: vod_id})
        return vod_info_dict
