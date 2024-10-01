from django.http import HttpResponseForbidden
from singapp.models import Sing

def sing_ownership_required(func):
    def decorated(request, *args, **kwargs):
        sing = Sing.objects.get(pk=kwargs['pk'])
        if not sing.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated