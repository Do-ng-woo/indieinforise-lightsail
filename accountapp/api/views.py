from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")  # SHA-256 해싱된 값이 넘어옴

        if not email or not password:
            return Response({"error": "이메일과 비밀번호를 입력하세요."}, status=400)

        # 📌 DB에서 사용자 조회
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "사용자가 존재하지 않습니다."}, status=400)

        # 📌 Django의 check_password 사용 (원본 vs SHA-256 비교 X)
        if not check_password(password, user.password):
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=400)

        # ✅ 로그인 성공 시 토큰 발급
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": {"id": user.id, "email": user.email, "nickname": user.nickname}})
    

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import F
from accountapp.models import CustomUser
from accountapp.api.serializers import UserSerializer
from myshowapp.models import UserPerformance
from myshowapp.api.serializers import UserPerformanceSerializer

class UserProfileAPIView(RetrieveAPIView):
    """🔑 로그인한 유저의 프로필 및 공연 관람 정보 반환 API"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 유저만 접근 가능
    authentication_classes = [TokenAuthentication]  # Token 인증 사용

    def get(self, request, *args, **kwargs):
        """유저 프로필 정보 + 유저의 공연 관람 기록 반환"""
        user = request.user  # 현재 로그인한 유저

        # 🎭 유저의 UserPerformance 필터링 및 정렬
        user_performances = UserPerformance.objects.filter(user=user).annotate(
            sort_date=Coalesce('article__datetime', 'article__date')  # 정렬을 위한 필드 추가
        ).order_by('-sort_date')

        # 📌 시리얼라이징 (유저 정보 + 공연 관람 정보)
        user_data = UserSerializer(user, context={'request': request}).data
        performance_data = UserPerformanceSerializer(user_performances, many=True, context={'request': request}).data

        return Response({
            "user": user_data,  # ✅ 유저 정보
            "performances": performance_data  # ✅ 유저의 공연 관람 정보 (최신순 정렬)
        })
    

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

User = get_user_model()

class OAuthLoginAPIView(APIView):
    """
    ✅ Google / Kakao / Naver 통합 로그인 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        provider = request.data.get("provider")  # "google", "kakao", "naver" 중 하나

        if not email or not provider:
            return Response({"error": "이메일과 OAuth 제공자를 입력해야 합니다."}, status=400)

        try:
            user = User.objects.get(email=email)
            # ✅ 기존 계정이 있으면 로그인 처리
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": "success",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "provider": provider
                }
            })
        except User.DoesNotExist:
            # ❌ 사용자가 없으면 회원가입 필요
            return Response({"status": "register", "email": email, "provider": provider})


class OAuthRegisterAPIView(APIView):
    """
    ✅ Google / Kakao / Naver 통합 회원가입 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        nickname = request.data.get("nickname")
        provider = request.data.get("provider")  # "google", "kakao", "naver"

        if not (email and nickname and provider):
            return Response({"error": "모든 필드를 입력해주세요."}, status=400)

        # 📌 이메일 중복 체크
        if User.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일입니다."}, status=400)

        # ✅ 회원가입 진행
        user = User.objects.create_user(email=email, nickname=nickname, password=None)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "status": "success",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "provider": provider
            }
        })

