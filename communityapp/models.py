from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument
from django.conf import settings

class Community(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='community', null=True)
    article= models.ManyToManyField(Article, related_name='community', blank=True)
    project = models.ManyToManyField(Project, related_name='community', blank=True)
    artist = models.ManyToManyField(Artist, related_name='community', blank=True)
    person = models.ManyToManyField(Person, related_name='community', blank=True)
    sing = models.ManyToManyField(Sing, related_name='community', blank=True)
    album = models.ManyToManyField(Album, related_name='community', blank=True)
    genre = models.ManyToManyField(Genre, related_name='community', blank=True)
    instrument = models.ManyToManyField(Instrument, related_name='community', blank=True)
    
    
    
    title = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='community/', null=True, blank=True)  # 수정됨
    content = models.TextField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    date = models.DateField(blank=True, null=True)  # 필수 입력 필드
    datetime = models.DateTimeField(blank=True, null=True)  # DateField에서 DateTimeField로 변경

    like = models.IntegerField(default=0)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
    BOARD_TYPES = (
        ('자유게시판', '자유게시판'),
        ('노래추천', '노래추천'),
        ('구인', '구인'),
        ('공연후기', '공연후기'),
        ('홍보', '홍보'),
    )
    board_type = models.CharField(
        max_length=50,
        choices=BOARD_TYPES,
        default='자유게시판',  # 기본값 설정
        verbose_name='게시판 종류'
    )
    
    def __str__(self):
        return f'{self.title}'

