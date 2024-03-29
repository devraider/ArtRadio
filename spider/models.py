from django.db import models
from datetime import datetime
from django.utils import timezone

class TrackModel(models.Model):
    track_id = models.AutoField(primary_key=True)
    radio_name = models.CharField(max_length=244)
    track_source = models.CharField(max_length=244)
    track_singer = models.CharField(max_length=244)
    track_name = models.CharField(max_length=244)
    track_yt_id = models.CharField(max_length=20, editable=True, null=True, blank=True)
    track_date = models.DateTimeField(auto_now=True, editable=True)
    track_date_updated = models.DateTimeField(default=timezone.now, editable=True)

    def __repr__(self):
        return self.track_id


class SpotifyModel(models.Model):
    spotify_id = models.ForeignKey(TrackModel, on_delete=models.CASCADE)
    # list of artists
    spotify_song_artists = models.TextField(null=True, blank=True)
    spotify_song_id = models.CharField(max_length=50, blank=True)
    # fields with URL value
    spotify_song_api = models.CharField(max_length=400, blank=True)
    spotify_song_external_urls = models.CharField(max_length=400, blank=True)
    spotify_song_preview = models.CharField(max_length=400, null=True, blank=True)
    spotify_song_thumbnail = models.CharField(max_length=400, blank=True)
    spotify_date = models.DateField(auto_now=True)
    updated_date = models.DateField(auto_now_add=datetime.now, editable=True)

