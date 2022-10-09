from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .track_extractor import TrackSources, TrackDetails, TrackExtractorImpuls, StreamMediaSpotify, StreamMediaYoutube
from .models import TrackModel, SpotifyModel
import logging

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
    # Youtube search by params or get a bell sound
    yt_search = StreamMediaYoutube().find_track(request.query_params.get("query", "kZ0M8hgRQag"))
    return Response(yt_search)


def spotify_handler_spider_radio() -> dict:
    """
    Just a function to keep steps for Spider to parse radio save and search track on Spotify.
    Used to be triggerd from AP Scheduler and View function.
    """
    t = TrackExtractorImpuls(TrackSources.IMPULS)
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
    t = TrackExtractorImpuls(TrackSources.IMPULS)
    details = TrackDetails(**t.get_track())
    # Insert track in database
    TrackModel.objects.update_or_create(**details.__dict__)
    return {k: str(v) for k, v in details.__dict__.items()}

