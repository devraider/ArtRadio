from django.db import models
from datetime import datetime


# Create your models here.
class HomeScreenModel(models.Model):
    label_id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=32)
    label_anchor = models.CharField(max_length=32)
    label_active = models.BooleanField(default=False)
    label_date = models.DateTimeField(auto_now_add=datetime.now, editable=True)


class SourceScreenModel(models.Model):
    source_id = models.AutoField(primary_key=True)
    source_label = models.ForeignKey(HomeScreenModel, related_name='source_screen', on_delete=models.CASCADE)
    source_name = models.CharField(max_length=64)
    source_key = models.CharField(max_length=64)
    source_thumbnail = models.URLField(max_length=244)
    source_date = models.DateTimeField(auto_now_add=datetime.now, editable=True)
