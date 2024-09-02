from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from instrumentapp.models import Instrument

class Subtitle(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomPersonManager(models.Manager):
    def get_or_create_person_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        all_subtitles = []
        for subtitle_name in normalized_subtitles:
            subtitle, created = Subtitle.objects.get_or_create(name=subtitle_name)
            all_subtitles.append(subtitle)

        person = self.filter(title__iexact=title.strip()).first()
        if not person:
            person = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if person:
            return person, False

        person = self.create(title=title.strip(), **defaults)
        person.sub_titles.set(all_subtitles)
        return person, True

class Person(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='person', null=True)
    title = models.CharField(max_length=20, null=False)
    sub_titles = models.ManyToManyField('Subtitle', related_name='persons', blank=True)
    image = models.ImageField(upload_to='person/', null=False)
    description = models.CharField(max_length=200, null=True)
    instruments = models.ManyToManyField(Instrument, related_name='persons', blank=True)  # 다룰 수 있는 악기
    
    like = models.IntegerField(default=0)
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
        
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드
    objects = CustomPersonManager()
    
    
    def __str__(self):
        return f'{self.title}'
    
        
        
class Description(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=100, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"
    
class PersonUpdateLog(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.person.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'