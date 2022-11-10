from django.contrib import admin
from .models import SpotifyModel, TrackModel
# Register your models here.

admin.site.register(SpotifyModel)
admin.site.register(TrackModel)
