from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
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
    SIGNUP_METHOD_CHOICES = (
        ('manual', 'Manual'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('kakao', 'Kakao'),
        ('naver', 'Naver'),
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

    privacy_policy_agreement = models.BooleanField(default=False)
    signup_method = models.CharField(max_length=20, choices=SIGNUP_METHOD_CHOICES, default='manual')  # 가입 방식

    def __str__(self):
        return self.username
    

class EmailUser(models.Model):
    email = models.EmailField(unique=True)  # 이메일 (고유)
    is_verified = models.BooleanField(default=False)  # 인증 완료 여부
    account_created = models.BooleanField(default=False)  # 계정이 만들어졌는지 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 생성된 시간
    token = models.CharField(max_length=50, blank=True, null=True)  # 인증 토큰 필드

    def is_expired(self):
        # 생성 후 10분이 지나면 만료로 간주
        return timezone.now() > self.created_at + timedelta(minutes=10)