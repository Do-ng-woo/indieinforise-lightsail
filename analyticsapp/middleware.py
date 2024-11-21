from .models import VisitorSession
from django.utils import timezone


class VisitorSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 세션 키가 없으면 생성
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        # 실제 클라이언트 IP 가져오기
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')

        # User-Agent 및 User 정보 가져오기
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_id = request.user.id if request.user.is_authenticated else None

        # 로드 밸런서 및 봇 요청 필터링
        ignored_user_agents = ["ELB-HealthChecker", "Googlebot", "Bingbot", "Pingdom"]
        ignored_ips = ["127.0.0.1"]  # 로드 밸런서 IP 목록 확장 가능

        if any(ua in user_agent for ua in ignored_user_agents) or ip_address in ignored_ips:
            return self.get_response(request)

        try:
            # VisitorSession 가져오거나 생성
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

        except Exception as e:
            # VisitorSession 생성/업데이트 실패 시 로그를 남길 수 있습니다.
            # 예: logging.error(f"VisitorSessionMiddleware error: {e}")
            pass

        # 다음 미들웨어/뷰 처리
        response = self.get_response(request)
        return response
