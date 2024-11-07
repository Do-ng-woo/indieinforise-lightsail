# analyticsapp/middleware.py

from .models import VisitorSession
from django.utils import timezone
from django.urls import resolve

class VisitorSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 세션 키가 존재하지 않으면 세션을 생성합니다.
        if not request.session.session_key:
            request.session.create()

        # 세션 키가 유효한 경우에만 VisitorSession을 생성합니다.
        session_key = request.session.session_key
        if session_key:
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            user_id = request.user.id if request.user.is_authenticated else None

            # 기존 세션이 있는지 확인
            session, created = VisitorSession.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'start_time': timezone.now(),
                    'page_views': 1
                }
            )

            # 기존 세션이면 페이지 방문 수 증가 및 종료 시간 업데이트
            if not created:
                session.page_views += 1
                session.end_time = timezone.now()
                session.save()
            else:
                # 새로운 세션 생성 시 초기 종료 시간 설정
                session.end_time = timezone.now()
                session.save()

        response = self.get_response(request)
        return response
