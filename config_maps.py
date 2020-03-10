# Class for config, allow for `item.config_thing` declarations

from music_objects import Track, Artist, Album
from logger import Logger

log = Logger('config_maps').info

class SearchConfig():

    def __init__(self, type_str, type_plural_str, typeClass):
        self.type = type_str
        self.types = type_plural_str
        self.typeClass = typeClass

def get_search_maps():
    track  = SearchConfig('track',  'tracks',  Track)
    artist = SearchConfig('artist', 'artists', Artist)
    album  = SearchConfig('album',  'albums',  Album)
    return (track, artist, album)
