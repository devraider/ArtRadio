# Generated by Django 4.1.1 on 2022-10-16 15:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0015_alter_trackmodel_track_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackmodel',
            name='track_date_updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]