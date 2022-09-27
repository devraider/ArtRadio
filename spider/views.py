from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .track_extractor import TrackSources, TrackDetails, TrackExtractorImpuls, StreamMediaSpotify
from .models import TrackModel, SpotifyModel


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
def spider_welcome(request):
    return Response("Welcome on ArtRadio Spider")


@api_view(['GET'])
def spider_radio(request):
    t = TrackExtractorImpuls(TrackSources.IMPULS)
    details = TrackDetails(**t.get_track())
    spotify_details = StreamMediaSpotify().find_track(details.radio_name)
    if not spotify_details.get("spotify_song_id"):
        return Response(spotify_details)
    # Save track details in Database
    track_details_model = TrackModel(**details.__dict__)
    track_details_model.save()
    # Add track details models as spotify Id to be added in database as Foreign Key
    spotify_details["spotify_id"] = track_details_model
    # Save spotify details in Database
    spotify_model = SpotifyModel(**spotify_details)
    spotify_model.save()
    # Delete spotify id because it was used only to for Database purpose
    del spotify_details["spotify_id"]
    return Response(spotify_details)
