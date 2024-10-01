

from profileapp.models import Profile
from django.contrib.auth.forms import AuthenticationForm

def profile_context(request):
    user_profile = None
    login_form = AuthenticationForm(request=request)  # request 파라미터 추가
    if request.user.is_authenticated:
        user_profile, created = Profile.objects.get_or_create(user=request.user)
    return {'user_profile': user_profile, 'login_form': login_form}
