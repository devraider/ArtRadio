import os
from typing import Dict, Protocol, Union, List, Callable, Type

import requests
from dataclasses import dataclass, field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pytube import Search as PytubeSearch, YouTube
from enum import Enum, auto
from time import time
from datetime import datetime
import logging
from fuzzywuzzy import process as fuzzy_process
from youtube_search import YoutubeSearch

# Instantiate logger because can not import logger from view
logger = logging.getLogger('spider.views')

# Custom Types
SEARCH_ENGINE = Type[Union[PytubeSearch, YoutubeSearch]]


# Custom Exceptions
class RadioRequestFailed(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


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
    track_singer: str = field(default_factory=str)
    track_yt_id: str = field(default_factory=str)
    track_name: str = field(default_factory=str)

    def __post_init__(self) -> None:
        """ Get singer and track name from radio stream name """
        try:
            self.track_singer, self.track_name = [name.strip() for name in self.radio_name.split(' - ', 1)]
        except ValueError:
            self.track_singer = "None"
            self.track_name = self.radio_name


class TrackExtractor(Protocol):

    def get_track(self) -> Dict[str, str]:
        ...


class TrackExtractorImpuls(TrackExtractor):
    def __init__(self, source: TrackSources):
        self.source = source

    def get_track(self) -> Dict[str, Union[str, time]]:
        """ Extract track from Impuls JSON """
        # result = self._do_request().json()
        return {
            "radio_name": "Nicole Cherry x Tata Vlad - Fum si scrum",
            "track_source": self.source

        }

    @staticmethod
    def _extract_track(result: Dict[str, str]) -> str:
        return result.get("title")

    def _do_request(self) -> requests.Response:
        res = requests.get(str(self.source.value), verify=False)
        if res.status_code not in (201, 200):
            raise RadioRequestFailed(f"Failed to fetch {self.source} with {res.status_code = }", res.status_code)
        return res


class TrackExtractorWithYtID(TrackExtractorImpuls):
    def __init__(self, source: TrackSources):
        super().__init__(source)

    def get_with_track_yt_id(self) -> Dict[str, Union[str, time]]:
        """ Add search and find YouTube track ID """
        track = self.get_track()
        yt_details = StreamMediaYoutube(YoutubeSearch).find_track(track.get("radio_name"))
        track['track_singer'] = yt_details['yt_song_artists']
        track['track_yt_id'] = yt_details["yt_song_id"]
        return track


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
        """ Get/ Find track details from Spotify """
        track_details = dict()
        # Fetch Spotify for given track and limit resp at 1
        track_details['spotify_date'] = datetime.now()
        #
        self.spotify_result = self.spotify.search(q=track_name, type="track", limit=1)
        # Get item details
        items = self.spotify_result.get("tracks", {}).get("items", [""])
        self.spotify_first_item = items[0] if items else {}
        # Build full dict with all details
        track_details.update({**self.__find_artist(), **self.__find_song(), **self.__find_song_thumbnail()})
        logger.debug(f"Track found {track_details}")
        return track_details

    def __find_artist(self) -> Dict[str, List[str]]:
        """ Find artist names """
        artists = {"spotify_song_artists": [""]}
        spotify_artists = self.spotify_first_item.get("artists")
        if spotify_artists:
            artists_list = [artists.get("name") for artists in spotify_artists]
            # Convert artist into string to be saved propery in database
            artists["spotify_song_artists"] = ",".join(artists_list)
        logger.debug(f"Artist found {artists}")
        return artists

    def __find_song(self) -> Dict[str, str]:
        """Find song song id, song api url in Spotify"""
        logger.debug(f"Loading song details")
        return {
            "spotify_song_id": self.spotify_first_item.get("id"),
            "spotify_song_api": self.spotify_first_item.get("href"),
            "spotify_song_external_urls": self.spotify_first_item.get("external_urls", {}).get("spotify"),
            "spotify_song_preview": self.spotify_first_item.get("preview_url"),
        }

    def __find_song_thumbnail(self) -> Dict[str, str]:
        """ Find song thumbnail in Spotify"""
        thumbnail = self.spotify_first_item.get("album", {}).get("images", [{}])[0]
        logger.debug(f"Thumbnail found: {thumbnail}")
        return {
            "spotify_song_thumbnail": thumbnail.get("url")
        }


class StreamMediaYoutube:
    def __init__(self, search_engine: SEARCH_ENGINE):
        self.yt_search = None
        self.stream = None
        self.yt_song_obj = None
        self.track_name = None
        self.search_engine = search_engine

    def find_track(self, track_name: str) -> Dict[str, Union[str,  datetime.now, None]]:
        """ Get/ Find track details from YouTube """
        # Add lyrics str to prevent VEVO (license) video to stream
        self.track_name = track_name
        self.search_song()
        self.yt_song_obj = self.__filter_search()
        if not self.yt_song_obj:
            return {}
        # Build track details
        track_details = dict()
        track_details['yt_date'] = datetime.now()
        track_details.update(**self.__find_song(), **self.__find_artist_and_song(), **self.__find_song_thumbnail())
        return track_details

    def search_song(self,):
        """ Search song on YouTube based on track name """
        # Prevent search of VEVO video to pass video license
        self.yt_search = self.search_engine(self.track_name)

    def __levenshtein_order_songs(self) -> fuzzy_process.extract:
        """ Order songs based Levenshtein Algorithm """
        track_name_lyrics = f"{self.track_name} official"
        songs_dict = {i: song.get("title") for i, song in enumerate(self.yt_search.videos)}
        return fuzzy_process.extract(track_name_lyrics, songs_dict)[:3]  # return only first 3 elements

    def __filter_search(self) -> Union[YouTube, None]:
        """
        Sometimes YT response is : The following content it's not available on this app.
        In this case we need to retry Search
        """
        levenshtein_list = self.__levenshtein_order_songs()
        for title, score, _index in levenshtein_list:
            # chosen_song = self.yt_search.results[_index] # for pytubeSearch
            chosen_song = self.yt_search.videos[_index]
            # check_mp3_status = self.__check_mp3_status(chosen_song.streams.get_audio_only("mp4").url) #pytubeSearch
            # check_thumbnail = self.__check_thumbnail(chosen_song.thumbnail_url)
            check_thumbnail = self.__check_thumbnail(chosen_song.get("thumbnails", [""])[0])
            # if all([check_thumbnail, check_mp3_status]):
            # if all([check_thumbnail]):
            #     self.download_song(chosen_song)
            #     return chosen_song
            return chosen_song
        return None

    @staticmethod
    def download_song(song_obj: YouTube):
        static = "./staticfiles/songs/"
        if os.path.exists(static):
            for file in os.listdir(static):
                os.remove(os.path.join(static, file))
        song_obj.streams.get_audio_only("mp4").download(filename=f"local_track_{song_obj.video_id}.mp4",
                                                        output_path=static)

    @staticmethod
    def __check_thumbnail(thumbnail_url: str, yt_retries: int = 3) -> bool:
        for yt_retried in range(yt_retries):
            if "hqdefault.jpg" not in thumbnail_url:
                return True
        return False

    @staticmethod
    def __check_mp3_status(mp3_url: str) -> bool:
        try:
            if r_status := requests.head(mp3_url).status_code == 200:
                return True
            logger.debug(f"Mp3 status is: {r_status}")
        except Exception as e:
            logger.debug(f"Mp3 check got exception {e}")
        return False
    # for pytubeSearch
    # def __find_song(self) -> Dict[str, str]:
    #     logger.debug(f"Loading song: {self.yt_song_obj.streams.get_audio_only('mp4')}")
    #     return dict(yt_song_id=self.yt_song_obj.video_id,
    #                 yt_song_mp4=self.yt_song_obj.streams.get_audio_only("mp4").url,
    #                 local_track_url=f"https://artradio-backend.herokuapp.com/static/songs/local_track_"
    #                                 f"{self.yt_song_obj.video_id}.mp4")

    def __find_song(self) -> Dict[str, str]:
        return dict(yt_song_id=self.yt_song_obj.get("id"))

    def __find_artist_and_song(self) -> Dict[str, str]:
        title = self.yt_song_obj.get("title")
        logger.debug(f"Loading artist details: {title}")
        artists = song_name = title
        if '-' in title:
            artists, song_name = title.split(" - ", 1)

        return {"yt_song_artists": artists.strip(),
                "yt_song_name": song_name.strip(),
                "yt_song_title": title}

    def __find_song_thumbnail(self) -> Dict[str, str]:
        thumbnails = self.yt_song_obj.get("thumbnails", [""])
        logger.debug(f"Loading thumbnail details: {thumbnails}")
        return {"yt_song_thumbnail": thumbnails[0]}
