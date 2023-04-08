import ffmpeg_util
import subprocess


def download_m3u8_video_url(url, file_name):
    return subprocess.call(ffmpeg_util.get_m3u8_video_url_command(url, file_name), shell=True)


def download_m3u8_video_url_slice(url, file_name, start_time, end_time):
    return subprocess.call(ffmpeg_util.get_m3u8_video_url_slice_command(url, file_name, start_time, end_time), shell=True)


def download_m3u8_video_file(m3u8_file_path, file_name):
    return subprocess.call(ffmpeg_util.get_m3u8_video_file_command(m3u8_file_path, file_name), shell=True)


def download_m3u8_video_file_slice(m3u8_file_path, file_name, start_time, end_time):
    return subprocess.call(ffmpeg_util.get_m3u8_video_file_slice_command(m3u8_file_path, file_name, start_time, end_time), shell=True)
