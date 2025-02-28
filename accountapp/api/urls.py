from django.urls import path
from .views import LoginAPIView,UserProfileAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('user/', UserProfileAPIView.as_view(), name='api_user_profile'),  # 🔥 유저 정보 조회 API 추가
]
