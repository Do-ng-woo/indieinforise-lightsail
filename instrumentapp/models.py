from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Subtitle(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomInstrumentManager(models.Manager):
    def get_or_create_instrument_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        all_subtitles = []
        for subtitle_name in normalized_subtitles:
            subtitle, created = Subtitle.objects.get_or_create(name=subtitle_name)
            all_subtitles.append(subtitle)

        instrument = self.filter(title__iexact=title.strip()).first()
        if not instrument:
            instrument = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if instrument:
            return instrument, False

        instrument = self.create(title=title.strip(), **defaults)
        instrument.sub_titles.set(all_subtitles)
        return instrument, True

class Instrument(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='instrument', null=True)
    title = models.CharField(max_length=20, null=False)
    image = models.ImageField(upload_to='instrument/', null=False, blank=False, default='default_image/default_profile.jpg')
    sub_titles = models.ManyToManyField('Subtitle', related_name='instruments', blank=True)
    content = models.TextField(null=True) 
    
    like = models.IntegerField(default=0)
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가
    
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    hide = models.BooleanField(default=False)  # 임시저장 여부를 나타내는 필드
    objects = CustomInstrumentManager()
    
    def __str__(self):
        return f'{self.title}'
    
        
        
class Description(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=100, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"
    
class InstrumentUpdateLog(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.instrument.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'