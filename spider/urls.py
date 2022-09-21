from django.urls import path
from . import views

urlpatterns = [
    path('wlc', views.spider_welcome, name="welcome_spider"),
    path('impuls', views.spider_radio, name="spider_radio")
]