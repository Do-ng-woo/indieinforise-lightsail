from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import get_object_or_404
from .models import EmailUser, CustomUser
from django.utils import timezone

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user_email = sociallogin.user.email

        if user_email:
            try:
                # 기존 사용자가 존재하는지 확인
                existing_user = CustomUser.objects.get(email=user_email)

                # 소셜 계정을 기존 사용자와 연결
                if not SocialAccount.objects.filter(user=existing_user, provider=sociallogin.account.provider).exists():
                    sociallogin.connect(request, existing_user)

                # EmailUser 업데이트
                email_user, created = EmailUser.objects.get_or_create(email=user_email)
                if created or not email_user.is_verified:
                    email_user.is_verified = True
                    email_user.account_created = True
                    email_user.created_at = timezone.now()
                    email_user.save()

            except CustomUser.DoesNotExist:
                # 기존 사용자가 없는 경우에만 EmailUser를 새로 생성
                email_user, created = EmailUser.objects.get_or_create(email=user_email)
                if created or not email_user.is_verified:
                    email_user.is_verified = True
                    email_user.account_created = True
                    email_user.created_at = timezone.now()
                    email_user.save()

        # 소셜 로그인 방식에 따라 signup_method 설정
        user = sociallogin.user
        if isinstance(user, CustomUser):
            provider = sociallogin.account.provider

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
