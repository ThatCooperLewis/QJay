import os, json, requests, logging
import wget
import kivy
import spotipy
import spotipy.util as util

def pretty_print_json(blob: dict):
    print(json.dumps(blob, indent=4, sort_keys=True))

def return_none(none_count=1):
    # For initializing empty class variables in bulk
    return tuple(None for x in range(none_count))


class SpotipyClient():

    # The sole purpose of this class is to authenticate the client's 
    # connection to Spotify API, so it can be passed into other classes 

    def __init__(self):
        username = self._get_spotipy_env('SPOTIPY_USERNAME')
        scope    = self._get_spotipy_env('SPOTIPY_SCOPE')
        token    = util.prompt_for_user_token(username, scope)

        if token:   self.client = spotipy.Spotify(auth=token)
        else:       self._alert_missing('Spotipy authentication token'); exit()

    def _get_spotipy_env(self, var_name):
        # Get necessary environment variables
        # If they don't exist, raise log alert and exit
        env_var = os.getenv(var_name, default=False)
        if env_var:     return env_var
        else:           self._alert_missing(var_name); exit()

    def _alert_missing(self, var_name):
        logging.error('Missing the necessary config for {}'.format(var_name))
        return False

    def get_client(self):
        return self.client


class Track():

    # This bad boy makes parsing track blobs easier
    # Pass in your typical track dictionary from Spotipy 

    def __init__(self, track_dict):
        self.name, self.artist_list, self.album, self.cover, self.cover_sm = return_none(5)
        self.is_playing, self.duration, self.elapsed, self.uri = return_none(4)
        self.update(track_dict)

    def update(self, track_dict):
        item = track_dict['item']
        self.uri        = item['uri']
        self.name       = item['name']
        self.album      = item['album']['name']
        self.duration   = item['duration_ms']
        self.elapsed    = track_dict['progress_ms']
        self.is_playing = track_dict['is_playing']
        self.cover      = item['album']['images'][0]['url']
        self.cover_sm   = item['album']['images'][2]['url']
        # Get a string and iterable list of multiple artists (if applicable)
        self.artist, self.artist_list = self._parse_artists(item['artists'])

    def _parse_artists(self, artists):
        artist_str, artist_list = '', []
        for index, artist in enumerate(artists):
            name = artist['name']
            artist_list.append('name')
            artist_str += name
            if index < (len(artists) - 1): artist_str += ', '
        return artist_str, artist_list


class NowPlaying():

    # Get info about & manipulate the currently-playing music

    def __init__(self, client):
        self.client = client
        self.track = Track(self.client.current_user_playing_track())
    
    def clean_track_dict(self, track_dict):
        # Remove verbose (and useless) lists from the track dict
        # For debugging purposes only
        track_dict.pop('available_markets', None)
        track_dict['item'].pop('available_markets', None)
        track_dict['item']['album'].pop('available_markets', None)
        return track_dict

    def get_track(self, init=False):
        result = self.client.current_playback()
        clean_result = self.clean_track_dict(result)
        self.track.update(clean_result)
        return self.track

    def get_track_art(self):
        image_url = self.track.cover
        logging.info('ALBUM IMAGE URL: {}'.format(image_url))
        return image_url

    def save_track_art(self, filepath='current.jpg'):
        if os.path.isfile(filepath): os.remove(filepath)
        filename = wget.download(self.track.cover, out=filepath, bar=None)
        return filename

    def next(self):
        logging.info('Playing next song')
        self.client.next_track()

    def previous(self):
        logging.info('Playing previous song')
        self.client.previous_track()

    def shuffle(self, state: bool):
        self.client.shuffle(state)
    
    def repeat(self, mode='context'):
        if mode not in ['context', 'track', 'off']:
            logging.error('NowPlaying: Invalid mode provided to track-repeat function. Only off/track/context allowed!')
            exit()
        self.client.repeat(mode)

if __name__ == '__main__':
    sp_client = SpotipyClient().client
    playing   = NowPlaying(sp_client)
    playing.repeat('poop')
    # path = playing.save_track_art()
    # playing.shuffle(True)
