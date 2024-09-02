from django.http import HttpResponseForbidden
from albumapp.models import Album

def album_ownership_required(func):
    def decorated(request, *args, **kwargs):
        album = Album.objects.get(pk=kwargs['pk'])
        if not album.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated