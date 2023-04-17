import re


def compute_clip_range(duration):
    # Computes the max offset using the vod duration in minutes
    return (duration * 60) + 2000


def extract_clip_offsets(clip_url):
    # Returns the offset of a clip url.
    return re.search(r'(?:-offset|-index)-(\d+)', clip_url).group(1)  # https://clips-media-assets2.twitch.tv/41021330461-offset-5598.mp4 would return '5598'


def return_clip_formats(vod_id, reps):
    # Use list comprehension to add all clip url''s to a list called 'default_clip_list' that follow the specified format which was used from August 2016 - Present
    default_clip_list = [f"https://clips-media-assets2.twitch.tv/{vod_id}-offset-{i}.mp4" for i in range(reps) if i % 2 == 0]

    # Use list comprehension to add all clip url''s to a list called 'alternate_clip_list' that follow the specified format. The vod_id in this case refers to the original vod id given by twitch.
    alternate_clip_list = [f"https://clips-media-assets2.twitch.tv/vod-{vod_id}-offset-{i}.mp4" for i in range(reps) if i % 2 == 0]

    # Use list comprehension to add all clip url''s to a list called 'legacy_clip_list' that follow the specified format which was used from May 25th, 2016 - August 2016
    legacy_clip_list = [f"https://clips-media-assets2.twitch.tv/{vod_id}-index-{int('000000000') + i:010}.mp4" for i in range(reps)]

    # dictionary to hold a key, value pair where the key is a counter and the value is the list
    clip_format_dict = {
        "1": default_clip_list,
        "2": alternate_clip_list,
        "3": legacy_clip_list
    }

    # return the dictionary
    return clip_format_dict


def return_all_clip_urls(clip_dict, clip_format):
    # Initialize a list called 'clip_url_list'
    clip_url_list = []

    # Loop through the dictionary and combine each list together based on the clip formats provided
    for key, value in clip_dict.items():
        if key in clip_format:
            clip_url_list += value
    # Return the list 'clip_url_list'
    return clip_url_list
