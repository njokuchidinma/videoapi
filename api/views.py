import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import UploadSerializer, TranscriptionSerializer
from .models import Video
from rest_framework import generics



class VideoUploadAPIView(generics.ListCreateAPIView):
    serializer_class = UploadSerializer
    queryset = Video.objects.all()


class VideoPlaybackAPIView(APIView):
    def get(self, request, video_id, format=None):
        video = get_object_or_404(Video, pk=video_id)
    
        video_path = os.path.join(settings.MEDIA_ROOT, str(video.upload_video))

        if not os.path.isfile(video_path):
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        try:

            response = video.upload_video.url
            return Response(response)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
