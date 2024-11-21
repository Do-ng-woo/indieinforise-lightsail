from django.db import models
from django.utils import timezone

class VisitorSession(models.Model):
    user_id = models.CharField(max_length=40, null=True, blank=True)  # 유저 ID나 식별자
    session_key = models.CharField(max_length=40, unique=True)        # 세션 고유 식별자
    ip_address = models.GenericIPAddressField()                       # IP 주소
    user_agent = models.TextField()                                   # 브라우저 정보
    start_time = models.DateTimeField(default=timezone.now)           # 방문 시작 시간
    end_time = models.DateTimeField(null=True, blank=True)            # 방문 종료 시간
    page_views = models.PositiveIntegerField(default=0)               # 방문한 페이지 수

    def __str__(self):
        return f"Session {self.session_key} - {self.start_time}"
    
    @property
    def duration(self):
        """방문자의 체류 시간 계산"""
        if self.end_time:
            return (self.end_time - self.start_time).seconds
        return 0
    
class DailyVisitorStatistics(models.Model):
    date = models.DateField(unique=True)
    homepage_views = models.PositiveIntegerField(default=0)  # 홈페이지 조회수
    total_visitors = models.PositiveIntegerField()
    max_duration = models.PositiveIntegerField()      # 최대 체류 시간 (초 단위)
    min_duration = models.PositiveIntegerField()      # 최소 체류 시간 (초 단위)
    avg_duration = models.FloatField()                # 평균 체류 시간 (초 단위)
    max_page_views = models.PositiveIntegerField()    # 최대 페이지 방문 수
    min_page_views = models.PositiveIntegerField()    # 최소 페이지 방문 수
    avg_page_views = models.FloatField()              # 평균 페이지 방문 수

    def __str__(self):
        return f"Statistics for {self.date}"