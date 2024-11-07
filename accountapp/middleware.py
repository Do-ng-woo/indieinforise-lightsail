from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class ProfileCompletionMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 로그인한 사용자인 경우
        if request.user.is_authenticated:
            user = request.user

            # 필수 정보가 누락된 경우
            if not user.gender or not user.birth_date or not user.purpose_of_use:
                # 현재 경로가 업데이트 페이지, 로그인 페이지, 로그아웃 페이지가 아닌 경우에만 리다이렉트
                if not request.path.startswith(reverse('accountapp:update', kwargs={'pk': user.pk})) and \
                   not request.path.startswith(reverse('accountapp:logout')) and \
                   not request.path.startswith(reverse('accountapp:login')):
                    return redirect('accountapp:update', pk=user.pk)
        
        return None