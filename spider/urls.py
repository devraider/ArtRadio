from django.urls import path
from . import views

urlpatterns = [
    path('wlc', views.spider_welcome, name="welcome_spider"),
    path('impuls', views.spider_radio, name="spider_radio"),
    path('yt_search', views.yt_spider_search, name="yt_spider_search"),
    path('yt_download', views.yt_download, name="yt_download")

]