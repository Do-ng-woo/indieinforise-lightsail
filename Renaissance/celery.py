from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django의 기본 설정 파일을 Celery에서 사용하도록 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Renaissance.settings')

# Celery 애플리케이션 생성
app = Celery('Renaissance')

# Django의 설정을 Celery에 적용
app.config_from_object('django.conf:settings', namespace='CELERY')

# 자동으로 Django 앱 내에서 tasks.py 파일을 찾도록 설정
app.autodiscover_tasks()


from celery.schedules import crontab

app.conf.beat_schedule = {
    'save-daily-statistics-every-midnight': {
        'task': 'analyticsapp.tasks.save_daily_statistics_task',
        'schedule': crontab(hour=0, minute=0),  # 매일 자정에 실행
    },
}