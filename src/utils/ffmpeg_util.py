import os

from config_util import load_config


def get_m3u8_video_url_command(url, file_name):
    ffmpeg_config = load_config()
    command = ffmpeg_config["FFMPEG"]["DOWNLOAD_M3U8_VIDEO_URL"].format(url, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    return command


def get_m3u8_video_url_slice_command(url, file_name, start_time, end_time):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_URL_SLICE"].format(start_time, end_time, url, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    return command


def get_m3u8_video_file_command(m3u8_file_path, file_name):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_FILE"].format(m3u8_file_path, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    return command


def get_m3u8_video_file_slice_command(m3u8_file_path, file_name, start_time, end_time):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_FILE_SLICE"].format(start_time, end_time, m3u8_file_path, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    return command
