from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import DailyVisitorStatistics, VisitorSession


class PageViewsFilter(admin.SimpleListFilter):
    title = _('Page Views')  # 필터 제목
    parameter_name = 'page_views'  # URL에서의 필터 매개변수 이름

    def lookups(self, request, model_admin):
        # 필터 옵션 정의
        return [
            ('1', _('1 View')),  # Page Views가 1인 항목
            ('>1', _('More than 1 View')),  # Page Views가 1보다 큰 항목
        ]

    def queryset(self, request, queryset):
        # 선택된 필터에 따라 queryset 필터링
        if self.value() == '1':
            return queryset.filter(page_views=1)
        elif self.value() == '>1':
            return queryset.filter(page_views__gt=1)
        return queryset


@admin.register(DailyVisitorStatistics)
class DailyVisitorStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'total_visitors', 'max_duration', 'min_duration',
        'avg_duration', 'max_page_views', 'min_page_views', 'avg_page_views','homepage_views'
    )
    ordering = ('-date',)  # 최신 날짜순으로 정렬
    list_filter = ('date',)  # 날짜 필터 추가
    search_fields = ('date',)  # 날짜 검색 기능 추가


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = (
        'session_key', 'user_id', 'start_time', 'end_time',
        'page_views', 'ip_address'
    )
    ordering = ('-start_time',)  # 최신 세션 순으로 정렬
    list_filter = ('start_time', PageViewsFilter)  # 세션 시작 시간 필터와 사용자 정의 필터 추가
    search_fields = ('session_key', 'user_id')  # 세션 키와 사용자 ID로 검색 가능
