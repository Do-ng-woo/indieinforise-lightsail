from django.db import models
from personapp.models import Person
from django.contrib.auth.models import User
from django.conf import settings


class Subtitle(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomArtistManager(models.Manager):
    def get_or_create_artist_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        # 주어진 title과 동일한 제목을 가진 아티스트가 있는지 대소문자를 구분하지 않고(iexact) 필터링하여 검색합니다.
        artist = self.filter(title__iexact=title.strip()).first()
        if not artist:
            artist = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if artist:
            return artist, False

        # 시그널에서 서브타이틀을 생성하고 연결하도록 아티스트만 생성합니다.
        artist = self.create(title=title.strip(), **defaults)
        return artist, True

class Artist(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='artist', null=True)
    title = models.CharField(max_length=200, null=False)
    sub_titles = models.ManyToManyField('Subtitle', related_name='artists', blank=True)
    image = models.ImageField(upload_to='artist/', null=False)
    description = models.CharField(max_length=200, null=True)
    person = models.ManyToManyField(Person, related_name='artist', blank=True)
    text_person = models.JSONField(default=list)  # JSON 필드로 변경
    
    like = models.IntegerField(default=0)
    hot_point = models.IntegerField(default=0)  # hot_point 필드 추가
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가

    created_at = models.DateField(auto_now_add=True, null=True)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드
    objects = CustomArtistManager()
    def __str__(self):
        return f'{self.title}'
    
        
class HonoraryEntry(models.Model):
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='honorary_entries')
    year = models.PositiveIntegerField()
    quarter = models.PositiveIntegerField(choices=[(1, '1분기'), (2, '2분기'), (3, '3분기'), (4, '4분기')])
    frame_style = models.CharField(max_length=100)  # 프레임 스타일을 나타내는 필드
    hot_point = models.IntegerField(default=0)  # 명예의 전당에서 받은 hot_point
    rank = models.PositiveIntegerField()  # 몇 등인지 기록할 필드
    category = models.CharField(max_length=6, choices=[('major', '메이저'), ('minor', '마이너')])  # 메이저/마이너 구분 필드

    class Meta:
        unique_together = ('artist', 'year', 'quarter', 'category')  # 동일 아티스트가 동일 분기에 중복으로 올라가는 것을 방지

    def __str__(self):
        return f'{self.artist.title} - {self.year} {self.get_quarter_display()}'
    
    
class Description(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=200, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"
    
class ArtistUpdateLog(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.artist.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'
    
class ArtistPointLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    points_used = models.IntegerField(default=0)  # 기본값 설정
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'artist')  # 사용자와 아티스트 조합은 유일해야 합니다.

    def __str__(self):
        return f'{self.user.username} - {self.artist.title} - {self.points_used}'
    
