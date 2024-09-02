
from django.http import HttpResponseForbidden
from communityapp.models import Community

def community_ownership_required(func):
    def decorated(request, *args, **kwargs):
        community = Community.objects.get(pk=kwargs['pk'])
        if not community.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated