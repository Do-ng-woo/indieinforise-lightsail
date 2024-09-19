from django.db import models
from django.contrib.auth.models import User
import requests
from django.conf import settings

class Subtitle(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return self.name
    
class CustomProjectManager(models.Manager):
    def get_or_create_project_by_subtitles(self, title, subtitles, defaults=None, **extra_fields):
        defaults = defaults or {}
        defaults.update(extra_fields)

        normalized_subtitles = set(subtitle.strip().lower() for subtitle in subtitles)

        # 주어진 title과 동일한 제목을 가진 아티스트가 있는지 대소문자를 구분하지 않고(iexact) 필터링하여 검색합니다.
        project = self.filter(title__iexact=title.strip()).first()
        if not project:
            project = self.filter(sub_titles__name__in=normalized_subtitles).distinct().first()

        if project:
            return project, False

        # 시그널에서 서브타이틀을 생성하고 연결하도록 아티스트만 생성합니다.
        project = self.create(title=title.strip(), **defaults)
        return project, True
    

class Project(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='project', null=True)
    title = models.CharField(max_length=200, null=False)
    sub_titles = models.ManyToManyField('Subtitle', related_name='project', blank=True)
    image = models.ImageField(upload_to='project/', null=False)
    description = models.CharField(max_length=200, null=True)
    latitude = models.FloatField(null=True)  # 위도 필드
    longitude = models.FloatField(null=True)  # 경도 필드
    address = models.CharField(max_length=100, null=True)  # 주소 필드
    
    like = models.IntegerField(default=0)
    views = models.IntegerField(default=0)  # 조회수 필드 추가
    comment_count = models.IntegerField(default=0)  # 댓글 수 필드 추가

    created_at = models.DateField(auto_now_add=True, null=True)
    hide = models.BooleanField(default=True)  # 임시저장 여부를 나타내는 필드
    objects = CustomProjectManager()
    
    def save(self, *args, **kwargs):
        if self.address:
            # 주소가 있는 경우 좌표로 변환
            coords = self.geocode_address(self.address)
            if coords:
                self.latitude, self.longitude = coords
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'

    def geocode_address(self, address):
        # 카카오 지도 API 키
        api_key = settings.KAKAO_API_KEY  # 여기에 카카오 API 키를 넣어주세요
        base_url = 'https://dapi.kakao.com/v2/local/search/address.json'

        headers = {
            'Authorization': f'KakaoAK {api_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://renaissance-zefht.run.goorm.site',  # 본인의 웹사이트 주소로 변경
            'KA': 'os/pc os_version/Windows 10 origin/https://renaissance-zefht.run.goorm.site',
        }

        # 카카오 지도 API 호출
        response = requests.get(base_url, params={'query': address}, headers=headers, verify=False)
        # API 응답 확인
        if response.status_code == 200:
            result = response.json()
            documents = result.get('documents', [])

            if documents:
                # 첫 번째 결과의 좌표 반환
                latitude, longitude = documents[0]['y'], documents[0]['x']
                
                return latitude, longitude
        
        return None

class Description(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='detailed_descriptions')
    name = models.CharField(max_length=100, default="정보")  # 정보의 이름을 위한 필드
    text = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.text}"

class ProjectUpdateLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='update_logs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField(blank=True, null=True)
    hide = models.BooleanField(default=True)  # 추가된 필드

    def __str__(self):
        return f'{self.project.title} - {self.updated_by} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'