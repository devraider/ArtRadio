# Generated by Django 4.1.1 on 2022-10-02 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0008_alter_spotifymodel_spotify_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifymodel',
            name='spotify_song_api',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='spotifymodel',
            name='spotify_song_artists',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spotifymodel',
            name='spotify_song_external_urls',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='spotifymodel',
            name='spotify_song_preview',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='spotifymodel',
            name='spotify_song_thumbnail',
            field=models.CharField(blank=True, max_length=400),
        ),
    ]