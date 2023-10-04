import os
import mimetypes
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser# import assemblyai as aai
import requests
import time
from moviepy.editor import VideoFileClip
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import UploadSerializer, TranscriptionSerializer
from .models import Video
from rest_framework import generics



# class VideoUploadAPIView(generics.ListCreateAPIView):
#     serializer_class = UploadSerializer
#     queryset = Video.objects.all()

# class VideoUploadAPIView(APIView):
#     serializer_class = UploadSerializer

#     def post(self, request, format=None):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             video_file = serializer.validated_data['upload_video']
            
#             # Generate a unique file name for the uploaded video
#             video_name = video_file.name  # You can change this to generate a unique name
#             video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_name)

            
#             # Save the video file to disk
#             with open(video_path, 'wb') as destination:
#                 for chunk in video_file.chunks():
#                     destination.write(chunk)

#             video_file = serializer.save()
            
#             return Response({"message": "Video uploaded successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, format=None):
        serializer = UploadSerializer(data=request.data)
        
        if serializer.is_valid():
            video_file = serializer.validated_data['upload_video']

            # Set the content type for streaming video
            content_type, encoding = mimetypes.guess_type(video_file.name)
            response = HttpResponse(self.stream_video(video_file), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(video_file.name)}"'

            # Save the video file to disk
            video_name = os.path.basename(video_file.name)
            video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_name)

            with open(video_path, 'wb') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def stream_video(self, video_file):
        # Implement logic to read and stream the video in chunks
        # You can adjust the chunk size as needed
        chunk_size = 8192

        with video_file.open('rb') as video:
            while True:
                data = video.read(chunk_size)
                if not data:
                    break
                yield data



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
        

class VideoTranscription(APIView):
    def get(self, request, video_id, format=None):
        video = get_object_or_404(Video, pk=video_id)
        video_path = os.path.join(settings.MEDIA_ROOT, str(video.upload_video))

        if not os.path.isfile(video_path):
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'audios')
            os.makedirs(audio_dir, exist_ok=True)

            audio_filename = f"{video_id}_audio.wav"
            audio_path = os.path.join(audio_dir, audio_filename)

            # Extract audio from video
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path)

            # Close the audio and video clips
            audio_clip.close()
            video_clip.close()

            base_url = "https://api.assemblyai.com/v2"

            headers = {
                "authorization": "a268bfecd28741d4a720febb1994aeb1" 
            }

            # Upload audio file to AssemblyAI
            with open(audio_path, "rb") as f:
                audio_response = requests.post(base_url + "/upload", headers=headers, data=f)

                upload_url = audio_response.json()["upload_url"]
            
            data = {
                "audio_url": upload_url
            }

            url = base_url + "/transcript"
            response = requests.post(url, json=data, headers=headers)

            transcript_id = response.json()['id']
            polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

            while True:
                transcription_result = requests.get(polling_endpoint, headers=headers).json()

                if transcription_result['status'] == 'completed':
                    break

                elif transcription_result['status'] == 'error':
                    raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

                else:
                    time.sleep(3)

            def get_subtitle_file(transcript_id, file_format):
                if file_format not in ["srt"]:
                    raise ValueError("Invalid file format. Valid formats are 'srt'")

                url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/{file_format}"

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    return response.text
                else:
                    raise RuntimeError(f"Failed to retrieve {file_format.upper()} file: {response.status_code} {response.reason}")

            # Call the function to get subtitle text
            subtitle_text = get_subtitle_file(transcript_id, "srt")
            # Include subtitle text in the API response
            response_data = {
                "subtitle": subtitle_text
            }

            return Response(response_data)
                
        except Exception as e:
            print(f"Error processing video ID {video_id}: {str(e)}")
                