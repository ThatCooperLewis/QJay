# Weird & stupid utility functions for various classes
import json

def pretty_print_json(blob: dict):
    # Debug tool
    print(json.dumps(blob, indent=4, sort_keys=True))


def milliseconds_to_mins(ms: int):
    ms = float(ms)
    seconds = int((ms/1000) % 60)
    seconds = "{:02d}".format(seconds)
    minutes = int((ms/(1000*60)) % 60)
    minutes = "{:02d}".format(minutes)
    return minutes, seconds
