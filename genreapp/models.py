from django.db import models
from django.contrib.auth.models import User
from artistapp.models import Artist
from singapp.models import Sing
from django.conf import settings

class Subtitle(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomGenreManager(models.Manager):
    def get_or_create_genre_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        all_subtitles = []
        for subtitle_name in normalized_subtitles:
            subtitle, created = Subtitle.objects.get_or_create(name=subtitle_name)
            all_subtitles.append(subtitle)

        genre = self.filter(title__iexact=title.strip()).first()
        if not genre:
            genre = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if genre:
            return genre, False

        genre = self.create(title=title.strip(), **defaults)
        genre.sub_titles.set(all_subtitles)
        return genre, True

class Genre(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='genre', null=True)
    title = models.CharField(max_length=20, null=False)
    sub_titles = models.ManyToManyField('Subtitle', related_name='genres', blank=True)
    content = models.TextField(null=True) 
    
    
    appearance_period = models.CharField(max_length=100, null=True) #출연시기
    period = models.CharField(max_length=100, null=True) #시대
    artist = models.ManyToManyField(Artist, related_name='genre', blank=True) #가수
    beginning_song = models.ManyToManyField(Sing, related_name='beginning_song', blank=True) #노래
    masterpiece_song = models.ManyToManyField(Sing, related_name='masterpiece_song', blank=True) #노래
    
    origins = models.ManyToManyField('self', related_name='originated_from', symmetrical=False, blank=True) #기원
    subgenres = models.ManyToManyField('self', related_name='parent_genres', symmetrical=False, blank=True) #하위장르
    derived_genres = models.ManyToManyField('self', related_name='derives_into', symmetrical=False, blank=True) #파생장르
    related_genres = models.ManyToManyField('self', related_name='related_to_genres', symmetrical=False, blank=True) #관련장르
    
    
    like = models.IntegerField(default=0)
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
        
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    hide = models.BooleanField(default=False)  # 임시저장 여부를 나타내는 필드
    objects = CustomGenreManager()
    
    def __str__(self):
        return f'{self.title}'
    
        
        
class Description(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=100, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"
    
class GenreUpdateLog(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.genre.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'