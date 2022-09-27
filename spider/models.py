from django.db import models


class TrackModel(models.Model):
    track_id = models.AutoField(primary_key=True)
    radio_name = models.CharField(max_length=50)
    track_source = models.CharField(max_length=50)
    track_singer = models.CharField(max_length=50)
    track_name = models.CharField(max_length=50)
    track_date = models.DateField()


class SpotifyModel(models.Model):
    spotify_id = models.ForeignKey(TrackModel, on_delete=models.CASCADE)
    # list of artists
    spotify_song_artists = models.TextField(null=True)
    spotify_song_id = models.CharField(max_length=50)
    # fields with URL value
    spotify_song_api = models.CharField(max_length=400)
    spotify_song_external_urls = models.CharField(max_length=400)
    spotify_song_preview = models.CharField(max_length=400)
    spotify_song_thumbnail = models.CharField(max_length=400)
    spotify_date = models.DateField()
    updated_date = models.DateField()

