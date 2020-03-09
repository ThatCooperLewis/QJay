# Standard Library
import os
import time
# Additional modules
import wget
import kivy
import spotipy
import spotipy.util as sputil
# Custom modules
import utils
from logger import Logger


class SpotipyClient():

    # The sole purpose of this class is to authenticate the client's
    # connection to Spotify API, so it can be passed into other classes

    def __init__(self):
        username = self._get_spotipy_env('SPOTIPY_USERNAME')
        scope = self._get_spotipy_env('SPOTIPY_SCOPE')
        token = sputil.prompt_for_user_token(username, scope)
        _log = Logger('SpotipyClient')
        self.error = _log.error

        if token:
            self.client = spotipy.Spotify(auth=token)
        else:
            self._alert_missing('Spotipy authentication token')
            exit()

    def _get_spotipy_env(self, var_name):
        # Get necessary environment variables
        # If they don't exist, raise log alert and exit
        env_var = os.getenv(var_name, default=False)
        if env_var:
            return env_var
        else:
            self._alert_missing(var_name)
            exit()

    def _alert_missing(self, var_name):
        self.error('Missing the necessary config for {}'.format(var_name))
        return False

    def get_client(self):
        return self.client


class Track():

    # This bad boy makes parsing track blobs easier
    # Pass in your typical playback dictionary from Spotipy.current_playback()

    def __init__(self, track_dict, playback_dict=None):
        if not track_dict:
            return
        self.update(track_dict, playback_dict)

    def update(self, track, playback_dict=None):
        self.uri = track['uri']
        self.name = track['name']
        self.duration = track['duration_ms']
        self.album = Album(track['album'])
        self.artist = Artist(track['artists'])
        if playback_dict:
            self.add_playback_metadata(playback_dict)

    def add_playback_metadata(self, playback_dict):
        self.elapsed = playback_dict['progress_ms']
        self.is_playing = playback_dict['is_playing']
        self.shuffle = playback_dict['shuffle_state']
        self.repeat = playback_dict['repeat_state']
        self.context_uri = playback_dict['context']['uri']


class Artist():

    def __init__(self, artist_list: list):
        self.update(artist_list)

    def update(self, artist_list):
        # TODO: figure out listed format
        self.name, self.name_list = self._parse_artist_names(artist_list)
        self.uri, self.uri_list = self._parse_artist_uris(artist_list)

    def _parse_artist_names(self, artists: list):
        artist_str, artist_list = '', []
        for index, artist in enumerate(artists):
            name = artist['name']
            artist_list.append(name)
            artist_str += name
            if index < (len(artists) - 1):
                artist_str += ', '
        return artist_str, artist_list

    def _parse_artist_uris(self, artists: list):
        # Set primary from first artist (usually most important)
        # Make a list of all of them
        primary_artist_uri = artists[0]['uri']
        artist_uri_list = []
        for artist in artists:
            artist_uri_list.append(artist['uri'])
        return primary_artist_uri, artist_uri_list


class Album():

    def __init__(self, album_dict, full_details=None):
        self.update(album_dict, full_details)

    def update(self, album, full_details=None):
        self.uri = album['uri']
        self.name = album['name']
        self.type = album['album_type']
        self.cover = album['images'][0]['url']
        self.cover_sm = album['images'][2]['url']
        self.artist = Artist(album['artists'])

    def add_full_details(self, album_details):
        return


class NowPlaying():

    # Get info about & manipulate the currently-playing music

    def __init__(self, client):
        self.client = client
        track_data, playback_data = self._get_current_data()
        self.track = Track(track_data, playback_dict=playback_data)
        # Declare logger class & shortcut its functions
        _log = Logger('NowPlaying')
        self.log = _log.info
        self.debug = _log.debug
        self.error = _log.error
        self.warn = _log.warn

    def _get_current_data(self):
        track_data = None
        playback_data = self.client.current_playback()
        if playback_data:
            track_data = playback_data.get('item')
        return track_data, playback_data

    def _refresh(self):
        playback_data = self.client.current_playback()
        track_data = playback_data['item']
        self.track.update(track_data, playback_data)
        self.debug('Updating current song...')
        self.debug('{0} - {1}'.format(self.track.name, self.track.artist))
        # TODO: Have this communicate with frontend, so visuals/text update in tandem

    def get_track(self):
        result = self.client.current_playback()
        clean_result = utils.clean_track_dict(result)
        self.track.update(clean_result)
        return self.track

    def get_track_art(self):
        image_url = self.track.album.cover
        self.log('Album URL - {}'.format(image_url))
        return image_url

    def save_track_art(self, filepath='current.jpg'):
        if os.path.isfile(filepath):
            os.remove(filepath)
        filename = wget.download(
            self.track.album.cover, out=filepath, bar=None)
        self.log('Album cover saved to {}'.format(filename))
        return filename

    def play_pause(self):
        self._refresh()
        if self.track.is_playing:
            self.client.pause_playback()
            self.log('Paused track')
        else:
            self.client.start_playback()
            self.log('Resumed track')

    def next(self):
        self.log('Playing next song')
        self.client.next_track()
        self._refresh()

    def previous(self):
        # NOTE: This doesn't start over the current song, like most "previous" buttons do
        self.log('Playing previous song')
        self.client.previous_track()
        self._refresh()

    def seek(self, ms_start):
        if ms_start > self.track.duration:
            self.warn('NowPlaying: Scrub position longer than song!')
            return
        self.client.seek_track(ms_start)

    def shuffle(self, state: bool):
        self.client.shuffle(state)

    def repeat(self, mode='context'):
        if mode not in ['context', 'track', 'off']:
            self.warn(
                'NowPlaying: Invalid mode provided for track-repeat')
            return
        self.log('Setting repeat mode to "{}"'.format(mode))
        self.client.repeat(mode)

    def get_sequencer_status(self):
        # Return the shuffle/play status of the current track
        self._refresh()
        return self.track.shuffle, self.track.repeat

    def get_progress(self):
        self._refresh()
        return utils.milliseconds_to_mins(self.track.elapsed)

    def set_volume(self, percent_vol):
        if not 0 <= percent_vol <= 100:
            self.warn('NowPlaying: Invalid volume level!')
            return
        self.client.volume(percent_vol)


class SearchTools():

    def __init__(self, client, limit=20):
        self.client = client
        self.limit = limit
        _log = Logger('SearchTools')
        self.log = _log.info

    def _search(self, query, typeString, typeClass):
        # Pass the proper type/class to search using a given query
        # Example: _search('Lady Gaga', 'artist', Artist)
        item_list = []
        result = self.client.search(query, type=typeString, limit=self.limit)
        result = utils.clean_track_dict(result)
        if result:
            result = result['{}s'.format(typeString)]['items']
            self.log('# of search results: {}'.format(len(result)))
            for item in result:
                item_list.append(typeClass(item))
            return item_list
        else:
            return None

    def set_results_limit(self, limit: int):
        self.limit = limit

    def get_album

    # def search_all(self, query):
        # return self._search(query, 'track,artist,album,playlist')

    def search_tracks(self, query):
        return self._search(query, 'track', Track)

    def search_artists(self, query):
        return self._search(query, 'artist', Artist)

    def search_albums(self, query):
        return self._search(query, 'album', Album)

    # def search_playlists(self, query):
        # return self._search(query, 'playlist')

    

if __name__ == '__main__':
    _log = Logger('QJay')
    log = _log.info
    sp_client = SpotipyClient().client
    playing = NowPlaying(sp_client)
    search = SearchTools(sp_client)
    tracklist = search.search_albums("King Gizzard")
    for track in tracklist:
        log(utils.pretty_print_album(track))
    # with open('output.json', 'w+') as fileboi:
        # fileboi.write(utils.pretty_print_json())
        # fileboi.close()
