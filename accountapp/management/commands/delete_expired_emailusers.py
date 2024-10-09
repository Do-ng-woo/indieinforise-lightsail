from django.core.management.base import BaseCommand
from accountapp.models import EmailUser
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = '10분이 지난 인증되지 않은 EmailUser 객체를 삭제합니다.'

    def handle(self, *args, **kwargs):
        # 10분이 지난 인증되지 않은 EmailUser 객체 조회 및 삭제
        expired_email_users = EmailUser.objects.filter(is_verified=False, created_at__lte=timezone.now() - timedelta(minutes=5))
        count = expired_email_users.count()
        expired_email_users.delete()
        self.stdout.write(self.style.SUCCESS(f'{count}개의 만료된 EmailUser 객체가 삭제되었습니다.'))