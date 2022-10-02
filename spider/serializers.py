from django.contrib.auth.models import User, Group
from .models import TrackModel, SpotifyModel
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SpotifyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyModel
        fields = ['spotify_song_artists', 'spotify_song_id', 'spotify_song_api',
                  'spotify_song_external_urls', 'spotify_song_preview', 'spotify_song_thumbnail',
                  'spotify_date', 'updated_date']
