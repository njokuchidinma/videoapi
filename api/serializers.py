from rest_framework import serializers
from rest_framework.serializers import FileField
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class UploadSerializer(serializers.ModelSerializer):
    upload_video = serializers.FileField()
    class Meta:
        model = Video
        fields = ['upload_video']

class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'url', 'transcription')