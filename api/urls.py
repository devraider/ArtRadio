from django.urls import path
from . import views

urlpatterns = [
    path('getSpotifySongs', views.get_spotify_songs, name="get_spotify_songs"),
]