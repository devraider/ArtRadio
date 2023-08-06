from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .track_extractor import TrackSources, TrackDetails, TrackExtractorImpuls, StreamMediaSpotify, StreamMediaYoutube,\
    ImpulsTrackExtractorWithYtID
from .models import TrackModel, SpotifyModel
import logging
from django.core.exceptions import ObjectDoesNotExist
from pytube import Search as PytubeSearch, YouTube
# Instantiate logger with file name
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
def spider_welcome(request) -> Response:
    return Response("Welcome on ArtRadio Spider")


@api_view(['GET'])
def spider_radio(request) -> Response:
    return Response(handler_spider_radio())


@api_view(["GET", "POST"])
def yt_spider_search(request):
    # YouTube search by params or get a bell sound
    songs_result = list()
    if request.POST:
        query_songs = request.body.get("querySongs")
        if query_songs:
            for song in query_songs:
                songs_result.append(StreamMediaYoutube(PytubeSearch).find_track(song))
    elif request.GET:
        yt_search = StreamMediaYoutube(PytubeSearch).find_track(request.query_params.get("query", "kZ0M8hgRQag"))
        songs_result.append(yt_search)
    logger.debug(f"Searched: {songs_result}")
    return Response(songs_result)


def your_view_function(request):
    mp3 = request.query_params.get("query", "kZ0M8hgRQag")
    file = open("", "rb").read()
    # response['Content-Disposition'] = 'attachment; filename=filename.mp3'
    return HttpResponse(file, mimetype="audio/mpeg")


def spotify_handler_spider_radio() -> dict:
    """
    Just a function to keep steps for Spider to parse radio save and search track on Spotify.
    Used to be triggerd from AP Scheduler and View function.
    """
    t = ImpulsTrackExtractorWithYtID(TrackSources.IMPULS)
    details = TrackDetails(**t.get_track())
    spotify_details = StreamMediaSpotify().find_track(details.radio_name)
    model_track, created_track = TrackModel.objects.update_or_create(**details.__dict__)
    if not spotify_details.get("spotify_song_id"):
        return spotify_details
    # Add track details models as spotify Id to be added in database as Foreign Key
    spotify_details["spotify_id"] = model_track
    # Save spotify details in Database
    model_spotify, created_spotify = SpotifyModel.objects.update_or_create(**spotify_details)
    # Delete spotify id because it was used only to for Database purpose
    del spotify_details["spotify_id"]
    logger.info(f"Spotify track was added {created_spotify!r} -> {model_spotify.__dict__}")
    return spotify_details


def handler_spider_radio() -> dict:
    """Extract track from IMPULS radio and save it to Database into TrackModel"""
    t = ImpulsTrackExtractorWithYtID(TrackSources.IMPULS)
    print(f"Something: {t.get_with_track_yt_id()}")
    details = TrackDetails(**t.get_with_track_yt_id())
    # Insert track in database
    try:
        if model := TrackModel.objects.get(radio_name=details.radio_name):
            print(f"model.track_yt_id{model.track_yt_id} => {details.track_yt_id}")
            if not model.track_yt_id:
                model.track_yt_id = details.track_yt_id
            model.track_date_updated = datetime.now()
            model.save()
        else:
            TrackModel(**details.__dict__).save()
    except ObjectDoesNotExist:
        logger.debug(f" Here should be inserted second/ duplicate obj {details.__dict__}")
        # TrackModel(**details.__dict__).save()
    logger.debug(f"TrackModel was added")
    return {k: str(v) for k, v in details.__dict__.items()}

