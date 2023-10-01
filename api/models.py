from django.db import models
from django.utils import timezone
# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    transcription = models.TextField(blank=True, null=True)
    upload_video = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(default=timezone.now)
