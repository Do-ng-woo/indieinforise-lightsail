from .models import VisitorSession
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)  # 로깅 설정


class VisitorSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # 정적 및 미디어 파일 요청 필터링
            if self.is_static_or_media_request(request.path):
                logger.debug(f"Filtered static/media request: {request.path}")
                return self.get_response(request)

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
                logger.info(f"Ignored request: IP={ip_address}, User-Agent={user_agent}")
                return self.get_response(request)

            # VisitorSession 생성 또는 업데이트
            self.handle_visitor_session(session_key, ip_address, user_agent, user_id)

        except Exception as e:
            # 예외 발생 시 로깅
            logger.error(f"Unhandled error in VisitorSessionMiddleware: {e}", exc_info=True)

        # 다음 미들웨어/뷰 처리
        return self.get_response(request)

    def is_static_or_media_request(self, path):
        """
        정적 파일(static) 또는 미디어 파일 요청 여부 확인
        """
        return path.startswith('/static/') or path.startswith('/media/')

    def get_client_ip(self, request):
        """
        클라이언트의 실제 IP 주소를 가져옵니다.
        """
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
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
        try:
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

            logger.info(
                f"{'Created' if created else 'Updated'} VisitorSession: "
                f"SessionKey={session_key}, IP={ip_address}, PageViews={session.page_views}"
            )

        except Exception as db_error:
            # 데이터베이스 관련 오류 로깅
            logger.error(
                f"Database error while handling VisitorSession: {db_error}, "
                f"SessionKey={session_key}, IP={ip_address}, User-Agent={user_agent}",
                exc_info=True,
            )
