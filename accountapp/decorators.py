from django.contrib.auth.models import User
from django.conf import settings
from django.apps import apps
from django.http import HttpResponseForbidden

def account_ownership_required(func):
    def decorated(request, *args, **kwargs):
        User = apps.get_model(settings.AUTH_USER_MODEL)  # User 모델을 동적으로 가져옵니다.
        user = User.objects.get(pk=kwargs['pk'])
        if not user == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated