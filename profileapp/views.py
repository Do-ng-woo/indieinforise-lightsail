from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from profileapp.forms import ProfileCreationForm
from profileapp.models import Profile

from django.utils.decorators import method_decorator
from profileapp.decorators import profile_ownership_required

from django.http import HttpResponseRedirect
from django.urls import reverse


class ProfileCreateView(CreateView):
    model = Profile
    context_object_name = 'target_profile'
    form_class = ProfileCreationForm
    template_name ='create.html'
    
    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('accountapp:detail', kwargs={'pk':self.object.user.pk})
        

@method_decorator(profile_ownership_required, 'get')
@method_decorator(profile_ownership_required, 'post')
class ProfileUpdateView(UpdateView):
    model = Profile
    context_object_name = 'target_profile'
    form_class = ProfileCreationForm
    template_name ='update.html'

    def get_success_url(self):
        return reverse_lazy('accountapp:detail', kwargs={'pk':self.object.user.pk})
    
def some_view(request):
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
    else:
        user_profile = None  # 사용자가 로그인하지 않았을 때의 처리
    return render(request, 'righter.html', {'user_profile': user_profile})

