from django.http import HttpResponseForbidden
from personapp.models import Person

def person_ownership_required(func):
    def decorated(request, *args, **kwargs):
        person = Person.objects.get(pk=kwargs['pk'])
        if not person.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated