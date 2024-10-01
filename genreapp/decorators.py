from django.http import HttpResponseForbidden
from genreapp.models import Genre

def genre_ownership_required(func):
    def decorated(request, *args, **kwargs):
        genre = Genre.objects.get(pk=kwargs['pk'])
        if not genre.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated