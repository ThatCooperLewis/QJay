# Weird & stupid utility functions for various classes
import json
from boltons.iterutils import remap


def milliseconds_to_mins(ms: int):
    ms = float(ms)
    seconds = int((ms/1000) % 60)
    seconds = "{:02d}".format(seconds)
    minutes = int((ms/(1000*60)) % 60)
    minutes = "{:02d}".format(minutes)
    return minutes, seconds


def parse_artists_dict(artists):
    artist_str, artist_list = '', []
    for index, artist in enumerate(artists):
        name = artist['name']
        artist_list.append('name')
        artist_str += name
        if index < (len(artists) - 1):
            artist_str += ', '
    return artist_str, artist_list


def clean_track_dict(track_dict):
    if track_dict:
        return remove_keys_from_dict(track_dict, ['available_markets', 'external_ids', 'preview_url', 'external_urls', 'href'])
    else:
        return None


def remove_keys_from_dict(input_dict, key_list: list):
    bad_keys = set(key_list)
    def drop_keys(path, key, value): return key not in bad_keys
    return remap(input_dict, visit=drop_keys)
