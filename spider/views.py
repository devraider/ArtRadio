from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .track_extractor import TrackSources, TrackDetails, TrackExtractorImpuls, StreamMediaSpotify
import json

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
    spotify = StreamMediaSpotify().find_track(details.radio_name)
    return Response(spotify)
