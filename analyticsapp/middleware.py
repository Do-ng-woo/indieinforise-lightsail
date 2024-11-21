from .models import VisitorSession
from django.utils import timezone

class VisitorSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 세션 키가 존재하지 않으면 세션을 생성합니다.
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        # IP 주소 가져오기 (실제 클라이언트 IP 우선)
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')

        # 로드 밸런서 또는 봇 요청 필터링
        ignored_user_agents = ["ELB-HealthChecker", "Googlebot", "Bingbot"]
        ignored_ips = ["127.0.0.1"]  # 로드 밸런서 상태 점검 IP 추가
        if any(ua in request.META.get("HTTP_USER_AGENT", "") for ua in ignored_user_agents) or ip_address in ignored_ips:
            return self.get_response(request)

        # User-Agent와 User 정보 가져오기
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_id = request.user.id if request.user.is_authenticated else None

        # VisitorSession 생성 또는 업데이트
        if session_key:
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

            if not created:
                # 기존 세션이면 페이지뷰 증가 및 종료 시간 업데이트
                session.page_views += 1
                session.end_time = timezone.now()
                session.save()
            else:
                # 새로운 세션 생성 시 초기 종료 시간 설정
                session.end_time = timezone.now()
                session.save()

        # 다음 미들웨어/뷰 처리
        response = self.get_response(request)
        return response
