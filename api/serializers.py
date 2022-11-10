from rest_framework import serializers
from .models import SourceScreenModel, HomeScreenModel


class SourceScreenModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceScreenModel
        fields = '__all__'


class HomeScreenModelSerializer(serializers.ModelSerializer):
    source_screen = SourceScreenModelSerializer(many=True, read_only=True)

    class Meta:
        model = HomeScreenModel
        fields = '__all__'
