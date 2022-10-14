from rest_framework.decorators import api_view
from rest_framework.response import Response
from spider.models import SpotifyModel, TrackModel
from spider.serializers import SpotifyModelSerializer, TrackModelSerializer
from .models import SourceScreenModel, HomeScreenModel
from .serializers import SourceScreenModelSerializer, HomeScreenModelSerializer
import logging


@api_view(['GET'])
def get_spotify_songs(requests) -> Response:
    """ Get a list with all songs from Spotify model"""
    spotify_obj = SpotifyModel.objects.all().order_by("-spotify_id")
    spotify_serializer = SpotifyModelSerializer(spotify_obj, many=True)
    return Response(spotify_serializer.data)


@api_view(['GET'])
def get_tracks(request) -> Response:
    """ Get a list with all tracks from radio"""
    tracks_obj = TrackModel.objects.all().order_by("-track_id")
    tracks_serializer = TrackModelSerializer(tracks_obj, many=True)
    return Response(tracks_serializer.data)


@api_view(['GET'])
def home_screen_ui(request) -> Response:
    home_screen_ui = HomeScreenModel.objects.all().order_by("-label_id")
    home_screen_ui_serialized = HomeScreenModelSerializer(home_screen_ui, many=True)
    return Response(home_screen_ui_serialized.data)



