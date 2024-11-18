from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from django.conf import settings



class Article(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='article', null=True)
    project = models.ManyToManyField(Project, related_name='article', blank=True)
    artist = models.ManyToManyField(Artist, related_name='article', blank=True)
    person = models.ManyToManyField(Person, related_name='article', blank=True)
    
    title = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='article/', null=False)
    content = models.TextField(null=True)
    link = models.URLField(max_length=500, null=True, blank=True)  # Link 필드 추가

    created_at = models.DateField(auto_now_add=True, null=True)
    date = models.DateField(blank=True, null=True)  # 필수 입력 필드
    datetime = models.DateTimeField(blank=True, null=True)  # DateField에서 DateTimeField로 변경
    running_time = models.IntegerField(blank=True, null=True)  # 공연 시간을 저장할 필드 추가 (단위: 분)
    
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
    like = models.IntegerField(default=0)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드


    def __str__(self):
        return f'{self.title}'

    #임베딩 저장 필드들
    # title_embedding = models.BinaryField(null=True, blank=True)  # 임베딩 저장 필드
    # content_embedding = models.BinaryField(null=True, blank=True)  # 임베딩 저장 필드
    # combined_text_embedding = models.BinaryField(null=True, blank=True)  # 출연, 장소, 날짜정보 포함 필드
    
    # def get_combined_text(self):
    #     project_names = ", ".join([project.title for project in self.project.all()])
    #     artist_names = ", ".join([artist.title for artist in self.artist.all()])
    #     date_str = self.datetime.strftime('%Y-%m-%d %H:%M') if self.datetime else self.date.strftime('%Y-%m-%d')
        
    #     combined_text = f"{project_names} {artist_names} {date_str}"
    #     return combined_text
    
class ArticleUpdateLog(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.article.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'
