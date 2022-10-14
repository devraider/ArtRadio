from django.urls import path
from . import views

urlpatterns = [
    path('getSpotifySongs', views.get_spotify_songs, name="get_spotify_songs"),
    path('getTracks', views.get_tracks, name="get_tracks"),
    path('homeScreen', views.home_screen_ui, name="home_screen_ui")
]