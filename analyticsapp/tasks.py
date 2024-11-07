from celery import shared_task
from .models import DailyVisitorStatistics, VisitorSession
from datetime import date, timedelta
from django.db.models import Max, Min, Avg, F

@shared_task
def save_daily_statistics_task():
    """하루가 끝날 때 일간 통계를 계산하여 저장"""
    target_date = date.today() - timedelta(days=1)  # 어제 날짜

    # 어제 날짜의 모든 세션 필터링
    sessions = VisitorSession.objects.filter(start_time__date=target_date)

    # 방문자 수
    total_visitors = sessions.count()

    if total_visitors == 0:
        # 방문자가 없는 경우 통계를 생성하지 않음
        return

    # 체류 시간 통계
    durations = sessions.annotate(duration=F('end_time') - F('start_time')).values_list('duration', flat=True)
    max_duration = max(durations, default=0).total_seconds() if durations else 0
    min_duration = min(durations, default=0).total_seconds() if durations else 0
    avg_duration = sum(d.total_seconds() for d in durations) / total_visitors if total_visitors > 0 else 0

    # 페이지 방문 통계
    page_view_stats = sessions.aggregate(
        max_views=Max('page_views'),
        min_views=Min('page_views'),
        avg_views=Avg('page_views')
    )

    # DailyVisitorStatistics 저장
    DailyVisitorStatistics.objects.create(
        date=target_date,
        total_visitors=total_visitors,
        max_duration=max_duration,
        min_duration=min_duration,
        avg_duration=avg_duration,
        max_page_views=page_view_stats['max_views'] or 0,
        min_page_views=page_view_stats['min_views'] or 0,
        avg_page_views=page_view_stats['avg_views'] or 0
    )