from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import get_object_or_404
from .models import EmailUser, CustomUser
from django.utils import timezone

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.utils import timezone
from .models import CustomUser, EmailUser
from django.contrib.auth import login
from django.utils.timezone import now

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        provider = sociallogin.account.provider

        # 이메일 처리
        user_email = user.email
        if user_email:
            try:
                # 기존 사용자가 존재하는지 확인
                existing_user = CustomUser.objects.get(email=user_email)

                # 소셜 계정을 기존 사용자와 연결
                if not SocialAccount.objects.filter(user=existing_user, provider=provider).exists():
                    sociallogin.account.user = existing_user
                    sociallogin.account.save()
                    sociallogin.user = existing_user  # 현재 세션에 기존 사용자 설정

                # 자동 로그인 처리
                login(request, existing_user)

                # EmailUser 업데이트
                email_user, created = EmailUser.objects.get_or_create(email=user_email)
                if created or not email_user.is_verified:
                    email_user.is_verified = True
                    email_user.account_created = True
                    email_user.created_at = now()
                    email_user.save()

                # 기존 사용자 처리 후 작업 종료
                return

            except CustomUser.DoesNotExist:
                # 기존 사용자가 없는 경우 EmailUser 생성
                email_user, created = EmailUser.objects.get_or_create(email=user_email)
                if created or not email_user.is_verified:
                    email_user.is_verified = True  # 이메일 인증 미완료 상태
                    email_user.account_created = True
                    email_user.created_at = now()
                    email_user.save()

        # 새로운 사용자 생성 로직
        if not sociallogin.is_existing:  # 기존 계정이 아닌 경우만 처리
            extra_data = sociallogin.account.extra_data
            if provider in ['kakao', 'naver']:
                # 닉네임 가져오기 (카카오, 네이버 공통 처리)
                nickname = extra_data.get('properties', {}).get('nickname', '') or \
                           extra_data.get('kakao_account', {}).get('profile', {}).get('nickname', '') or \
                           extra_data.get('nickname', '')

                if nickname:
                    user.username = nickname  # 닉네임을 사용자 이름으로 설정

            # 소셜 로그인 방식 설정
            if provider == 'google':
                user.signup_method = 'google'
            elif provider == 'facebook':
                user.signup_method = 'facebook'
            elif provider == 'kakao':
                user.signup_method = 'kakao'
            elif provider == 'naver':
                user.signup_method = 'naver'
            else:
                user.signup_method = 'manual'  # 수동으로 추가된 경우는 manual로 설정

            user.save()