from django.db import models
from django.contrib.auth.models import User
from artistapp.models import Artist
from django.conf import settings

class Subtitle(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomSingManager(models.Manager):
    def get_or_create_sing_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        all_subtitles = []
        for subtitle_name in normalized_subtitles:
            subtitle, created = Subtitle.objects.get_or_create(name=subtitle_name)
            all_subtitles.append(subtitle)

        sing = self.filter(title__iexact=title.strip()).first()
        if not sing:
            sing = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if sing:
            return sing, False

        sing = self.create(title=title.strip(), **defaults)
        sing.sub_titles.set(all_subtitles)
        return sing, True

class Sing(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='sing', null=True)
    title = models.CharField(max_length=200, null=False)
    sub_titles = models.ManyToManyField('Subtitle', related_name='sings', blank=True)
    image = models.ImageField(upload_to='sing/', null=False)
    content = models.TextField(null=True) #가사 내용을 위함
    datetime = models.DateTimeField(blank=True, null=True)  # 발매일을 위함    
    artist = models.ManyToManyField(Artist, related_name='sing', blank=True) #가수
    
    like = models.IntegerField(default=0)
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
        
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드
    objects = CustomSingManager()
    
    def __str__(self):
        return f'{self.title}'

        
        
class Description(models.Model):
    sing = models.ForeignKey(Sing, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=100, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"
    
class SingUpdateLog(models.Model):
    sing = models.ForeignKey(Sing, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.sing.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'