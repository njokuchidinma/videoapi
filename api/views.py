import os
import assemblyai as aai
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
                