import json
import utils
from logger import Logger

_log = Logger('debug_utils')
log = _log.info


def prettify_json(blob: dict):
    # Debug tool
    return json.dumps(blob, indent=4, sort_keys=True)


def prettify_track(trackObj):
    return '{} - {} - {}'.format(trackObj.name, trackObj.artist.name, trackObj.album.name)


def prettify_album(albumObj):
    return '{} - {} - {}'.format(albumObj.name, albumObj.artist.name, albumObj.type)


def print_diverse_results(result, ):
    for category, results in result.items():
        print(len(results))
        log('---- {} ----'.format(category))
        for item in results:
            if category == 'albums':
                log(prettify_album(item))
            elif category == 'tracks':
                log(prettify_track(item))
            else:
                log(item.name)


def write_dict_to_file(output_dict, filename='output.json'):
    with open(filename, 'w+') as fileboi:
        fileboi.write(prettify_json(output_dict))
        fileboi.close()
