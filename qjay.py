# Standard Library
import os
import logging
# Additional modules
import wget
import kivy
import spotipy
import spotipy.util as sputil
# Custom modules
import utils


class SpotipyClient():

    # The sole purpose of this class is to authenticate the client's
    # connection to Spotify API, so it can be passed into other classes

    def __init__(self):
        username = self._get_spotipy_env('SPOTIPY_USERNAME')
        scope = self._get_spotipy_env('SPOTIPY_SCOPE')
        token = sputil.prompt_for_user_token(username, scope)

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
        logging.error('Missing the necessary config for {}'.format(var_name))
        return False

    def get_client(self):
        return self.client


class Track():

    # This bad boy makes parsing track blobs easier
    # Pass in your typical playback dictionary from Spotipy.current_playback()

    def __init__(self, playback_dict):
        self.update(playback_dict)

    def update(self, track_dict):
        item = track_dict['item']
        self.uri = item['uri']
        self.name = item['name']
        self.album = item['album']['name']
        self.duration = item['duration_ms']
        self.elapsed = track_dict['progress_ms']
        self.is_playing = track_dict['is_playing']
        self.shuffle = track_dict['shuffle_state']
        self.repeat = track_dict['repeat_state']
        self.context_uri = track_dict['context']['uri']
        self.cover = item['album']['images'][0]['url']
        self.cover_sm = item['album']['images'][2]['url']
        # Get a string and iterable list of multiple artists (if applicable)
        self.artist, self.artist_list = self._parse_artists(item['artists'])

    def _parse_artists(self, artists):
        artist_str, artist_list = '', []
        for index, artist in enumerate(artists):
            name = artist['name']
            artist_list.append('name')
            artist_str += name
            if index < (len(artists) - 1):
                artist_str += ', '
        return artist_str, artist_list


class NowPlaying():

    # Get info about & manipulate the currently-playing music

    def __init__(self, client):
        self.client = client
        self.track = Track(self.client.current_playback())
        self.log = self._info_logging
        self.debug = self._debug_logging

    def _refresh(self):
        self.debug('Updating current song...')
        self.debug('{0} - {1}'.format(self.track.name, self.track.artist))
        self.track.update(self.client.current_playback())
        # TODO: Have this communicate with frontend, so visuals/text update in tandem

    def _debug_logging(self, message: str):
        # TODO: move this better place
        logging.debug('NowPlaying: {}'.format(message))

    def _info_logging(self, message: str):
        logging.info('NowPlaying: {}'.format(message))

    def get_track(self):
        result = self.client.current_playback()
        clean_result = utils.clean_track_dict(result)
        self.track.update(clean_result)
        return self.track

    def get_track_art(self):
        image_url = self.track.cover
        self.log('Album URL - {}'.format(image_url))
        return image_url

    def save_track_art(self, filepath='current.jpg'):
        if os.path.isfile(filepath):
            os.remove(filepath)
        filename = wget.download(self.track.cover, out=filepath, bar=None)
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
            logging.warning('NowPlaying: Scrub position longer than song!')
            return
        self.client.seek_track(ms_start)

    def shuffle(self, state: bool):
        self.client.shuffle(state)

    def repeat(self, mode='context'):
        if mode not in ['context', 'track', 'off']:
            logging.warning(
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
            logging.warning('NowPlaying: Invalid volume level!')
            return
        self.client.volume(percent_vol)


class SearchTools():

    def __init__(self, client, limit=20):
        self.client = client
        self.limit = limit

    def _search(self, query, search_type):
        result = self.client.search(query, type=search_type, limit=self.limit)
        return utils.clean_track_dict(result)

    def set_results_limit(self, limit: int):
        self.limit = limit

    def search_all(self, query):
        return self._search(query, 'track,artist,album,playlist')

    def search_songs(self, query):
        return self._search(query, 'track')

    def search_artists(self, query):
        return self._search(query, 'artist')

    def search_albums(self, query):
        return self._search(query, 'album')

    def search_playlists(self, query):
        return self._search(query, 'playlist')



if __name__ == '__main__':
    sp_client = SpotipyClient().client
    playing = NowPlaying(sp_client)
    search = SearchTools(sp_client)
    with open('output.json', 'w+') as fileboi:
        fileboi.write(utils.pretty_print_json(search.search_playlists("Coop's Scoops")))
        fileboi.close()
