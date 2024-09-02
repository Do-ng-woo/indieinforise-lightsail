from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile/', null=True, default='myarticleimage/default_profile.jpg')
    message = models.CharField(max_length=100, null=True)
    level = models.IntegerField(default=0)  # 사용자 등급
    points = models.IntegerField(default=0)  # 사용자 포인트
    post_count = models.IntegerField(default=0)  # 작성한 글 수
    comment_count = models.IntegerField(default=0)  # 작성한 댓글 수
    