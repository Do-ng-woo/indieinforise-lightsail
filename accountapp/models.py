from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.
class HelloWorld(models.Model):
    text = models.CharField(max_length=255, null=False)
    
class FavoriteSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    search_field = models.CharField(max_length=100)
    keyword = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'search_field', 'keyword')

    def __str__(self):
        return f"{self.user.username}: {self.search_field} - {self.keyword}"
    
class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    purpose_of_use = models.CharField(max_length=100, null=True, blank=True)
    
    image = models.ImageField(upload_to='profile/', null=True, default='myarticleimage/default_profile.jpg')
    message = models.CharField(max_length=100, null=True)
    level = models.IntegerField(default=0)  # 사용자 등급
    points = models.IntegerField(default=0)  # 사용자 포인트
    post_count = models.IntegerField(default=0)  # 작성한 글 수
    comment_count = models.IntegerField(default=0)  # 작성한 댓글 수
    
    performance_points = models.IntegerField(default=0)  # 공연 포인트 필드 추가 공연을 사용자가 몇분이나 봤는지를 저장