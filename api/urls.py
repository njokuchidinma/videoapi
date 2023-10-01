# from django.urls import path
# from rest_framework import routers
# from .views import VideoPlaybackView, VideoUploadViewSet



# router = routers.DefaultRouter()
# router.register(r'upload', VideoUploadViewSet, basename="upload")

# urlpatterns = [
#     path('playback/<int:pk>/', VideoPlaybackView.as_view(), name='playback'),
# ]

# urlpatterns += router.urls\

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('api/upload/', views.VideoUploadAPIView.as_view(), name='video_upload'),
    path('api/playback/<int:video_id>/', views.VideoPlaybackAPIView.as_view(), name='video_playback'),
    path('api/transcription/<int:video_id>/', views.VideoTranscription.as_view(), name='video-transcription'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)