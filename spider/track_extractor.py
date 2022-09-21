import os
from typing import Dict, Protocol, Union, List

import requests
from dataclasses import dataclass, field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from enum import Enum, auto
from time import time
from collections import ChainMap

class TrackSources(Enum):
    """ Radio sources """
    KISSFM = auto()
    DIGIFM = auto()
    IMPULS = 'https://www.radioimpuls.ro/title-updater.php'


@dataclass
class TrackDetails:
    """ Dataclass with track info and source """
    radio_name: str
    track_source: TrackSources
    track_singer: str = field(init=False)
    track_name: str = field(init=False)
    track_date: time

    def __post_init__(self) -> None:
        """ Get singer and track name from radio stream name """
        try:
            self.track_singer, self.track_name = self.radio_name.split('-')
        except ValueError:
            self.track_singer = ""
            self.track_name = ""


class TrackExtractor(Protocol):

    def get_track(self) -> Dict[str, str]:
        ...


class TrackExtractorImpuls(TrackExtractor):
    def __init__(self, source: TrackSources):
        self.source = source

    def get_track(self) -> Dict[str, Union[str, time]]:
        result = self._do_request().json()
        return {
            "radio_name": self._extract_track(result),
            "track_source": self.source,
            "track_date": time()

        }

    @staticmethod
    def _extract_track(result: Dict[str, str]) -> str:
        return result.get("title")

    def _do_request(self) -> requests.Response:
        return requests.get(str(self.source.value), verify=False)


class StreamMedia(Protocol):
    def find_track(self):
        ...


class StreamMediaSpotify:
    def __init__(self):
        self.spotify_first_item = None
        self.spotify_result = None
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_ID"),
            client_secret=os.environ.get("SPOTIFY_SECRET"),
            redirect_uri=os.environ.get("SPOTIFY_URI")
            )
        )

    def find_track(self, track_name: str):
        track_details = dict()
        # Fetch Spotify for given track and limit resp at 1
        self.spotify_result = self.spotify.search(q=track_name, type="track", limit=1)
        # Get item details
        # print(self.spotify_result.get("tracks", {}).get("items", [""]))
        self.spotify_first_item = self.spotify_result.get("tracks", {}).get("items", [""])[0]
        # Build full dict with all details
        # track_details.update({**self.__find_artist(), **self.__find_song(), **self.__find_song_thumbnail()})
        for details in [self.__find_artist(), self.__find_song(), self.__find_song_thumbnail()]:
            track_details.update(details)
        return track_details

    def __find_artist(self) -> Dict[str, List[str]]:
        artists = {"spotify_song_artists": [""]}
        spotify_artists = self.spotify_first_item.get("artists")
        if spotify_artists:
            artists["spotify_song_artists"] = [artists for artists in spotify_artists]
        return artists

    def __find_song(self) -> Dict[str,str]:
        return {
            "spotify_song_id": self.spotify_first_item.get("id"),
            "spotify_song_api": self.spotify_first_item.get("href"),
            "spotify_song_external_urls": self.spotify_first_item.get("external_urls"),
            "spotify_song_preview": self.spotify_first_item.get("preview_url"),
        }

    def __find_song_thumbnail(self):
        return {
            "spotify_song_id": self.spotify_first_item.get("album", {}).get("images", [""])[0]
        }
