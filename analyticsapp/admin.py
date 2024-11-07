from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DailyVisitorStatistics, VisitorSession

@admin.register(DailyVisitorStatistics)
class DailyVisitorStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_visitors', 'max_duration', 'min_duration', 'avg_duration', 'max_page_views', 'min_page_views', 'avg_page_views')
    ordering = ('-date',)  # 최신 날짜순으로 정렬
    list_filter = ('date',)  # 날짜 필터 추가
    search_fields = ('date',)  # 날짜 검색 기능 추가

@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user_id', 'start_time', 'end_time', 'page_views', 'ip_address')
    ordering = ('-start_time',)  # 최신 세션 순으로 정렬
    list_filter = ('start_time',)  # 세션 시작 시간 필터 추가
    search_fields = ('session_key', 'user_id')  # 세션 키와 사용자 ID로 검색 가능