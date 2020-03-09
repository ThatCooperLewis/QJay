# Weird & stupid utility functions for various classes
import json
from boltons.iterutils import remap

def pretty_print_json(blob: dict):
    # Debug tool
    return json.dumps(blob, indent=4, sort_keys=True)


def milliseconds_to_mins(ms: int):
    ms = float(ms)
    seconds = int((ms/1000) % 60)
    seconds = "{:02d}".format(seconds)
    minutes = int((ms/(1000*60)) % 60)
    minutes = "{:02d}".format(minutes)
    return minutes, seconds

def clean_track_dict(track_dict):
    return remove_keys_from_dict(track_dict, ['available_markets', 'external_ids', 'preview_url', 'external_urls', 'href'])

def remove_keys_from_dict(input_dict, key_list: list):
    bad_keys = set(key_list)
    drop_keys = lambda path, key, value: key not in bad_keys
    return remap(input_dict, visit=drop_keys)
