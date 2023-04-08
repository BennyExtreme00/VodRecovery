import subprocess
import os

from config_util import load_config


def download_m3u8_video_url(url, file_name):
    ffmpeg_config = load_config()
    command = ffmpeg_config["FFMPEG"]["DOWNLOAD_M3U8_VIDEO_URL"].format(url, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_url_slice(url, file_name, start_time, end_time):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_URL_SLICE"].format(start_time, end_time, url, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_file(m3u8_file_path, file_name):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_FILE"].format(m3u8_file_path, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    subprocess.call(command, shell=True)


def download_m3u8_video_file_slice(m3u8_file_path, file_name, start_time, end_time):
    ffmpeg_config = load_config()
    command = ffmpeg_config["DOWNLOAD_M3U8_VIDEO_FILE_SLICE"].format(start_time, end_time, m3u8_file_path, os.path.join(load_config()["DIRECTORIES"]["DEFAULT_DIRECTORY"], file_name))
    subprocess.call(command, shell=True)
