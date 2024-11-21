from .models import VisitorSession
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)  # 로깅 설정

class VisitorSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # 세션 키 생성 (없으면 새로 생성)
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            # 클라이언트 IP 가져오기
            ip_address = self.get_client_ip(request)

            # User-Agent 및 User 정보 가져오기
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            user_id = request.user.id if request.user.is_authenticated else None

            # 로드 밸런서 및 봇 요청 필터링
            if self.is_ignored_request(ip_address, user_agent):
                return self.get_response(request)

            # VisitorSession 생성 또는 업데이트
            self.handle_visitor_session(session_key, ip_address, user_agent, user_id)

        except Exception as e:
            # 예외 발생 시 로깅
            logger.error(f"Error in VisitorSessionMiddleware: {e}", exc_info=True)

        # 다음 미들웨어/뷰 처리
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        클라이언트의 실제 IP 주소를 가져옵니다.
        """
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        return ip_address

    def is_ignored_request(self, ip_address, user_agent):
        """
        로드 밸런서 및 봇 요청을 필터링합니다.
        """
        ignored_user_agents = ["ELB-HealthChecker", "Googlebot", "Bingbot", "Pingdom"]
        ignored_ips = ["127.0.0.1"]  # 로드 밸런서 및 테스트 IP 확장 가능

        return (
            any(bot in user_agent for bot in ignored_user_agents)
            or ip_address in ignored_ips
        )

    def handle_visitor_session(self, session_key, ip_address, user_agent, user_id):
        """
        VisitorSession을 생성하거나 업데이트합니다.
        """
        session, created = VisitorSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'start_time': timezone.now(),
                'end_time': timezone.now(),
                'page_views': 1,
            },
        )

        if not created:
            # 기존 세션: 페이지뷰 증가 및 종료 시간 갱신
            session.page_views += 1
            session.end_time = timezone.now()
            session.save()
