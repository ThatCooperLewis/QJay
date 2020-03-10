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

    def __init__(self, artists):
        self.update(artists)

    def update(self, artists):
        self.name, self.name_list = self._parse_artist_names(artists)
        self.uri, self.uri_list = self._parse_artist_uris(artists)

    def _parse_artist_names(self, artists):
        artist_str, artist_list = '', []
        if type(artists) is list:
            for index, artist in enumerate(artists):
                name = artist['name']
                artist_list.append(name)
                artist_str += name
                if index < (len(artists) - 1):
                    artist_str += ', '
        else: 
            artist_str = artists['name']
            artist_list.append(artist_str)
        return artist_str, artist_list

    def _parse_artist_uris(self, artists: list):
        # Set primary from first artist (usually most important)
        # Make a list of all of them
        artist_uri_list = []
        if type(artists) is list:
            primary_artist_uri = artists[0]['uri']
            for artist in artists:
                artist_uri_list.append(artist['uri'])
        else:
            primary_artist_uri = artists['uri']
            artist_uri_list.append(primary_artist_uri)
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
        # For extra songs n shit
        return
