from django.http import HttpResponseForbidden
from artistapp.models import Artist

def artist_ownership_required(func):
    def decorated(request, *args, **kwargs):
        artist = Artist.objects.get(pk=kwargs['pk'])
        if not artist.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated