from django.http import HttpResponseForbidden
from instrumentapp.models import Instrument

def instrument_ownership_required(func):
    def decorated(request, *args, **kwargs):
        instrument = Instrument.objects.get(pk=kwargs['pk'])
        if not instrument.writer == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated