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
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class GoogleLoginAPIView(APIView):
    """🔑 Google 로그인 API"""

    def post(self, request):
        id_token = request.data.get("id_token")

        # ✅ Google OAuth2 API로 ID Token 검증
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        google_response = requests.get(google_url)

        if google_response.status_code != 200:
            return Response({"error": "Google 인증 실패"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = google_response.json()
        email = user_data.get("email")
        name = user_data.get("name")
        picture = user_data.get("picture")

        if not email:
            return Response({"error": "Google에서 이메일을 가져올 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 유저 생성 또는 가져오기
        user, created = User.objects.get_or_create(email=email, defaults={"username": email, "name": name})

        # ✅ JWT 토큰 생성
        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "email": user.email,
                "name": user.name,
                "profile_image": picture,
            },
        }, status=status.HTTP_200_OK)

