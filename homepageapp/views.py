from django.shortcuts import render
# Create your views here.
# Create your views here.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView,TemplateView

from homepageapp.models import Homepage
from homepageapp.forms import HomepageCreationForm
from django.urls import reverse
from django.utils import timezone
from django.db.models.functions import Coalesce

from articleapp.models import Article
from artistapp.models import Artist
from projectapp.models import Project
from communityapp.models import Community
from personapp.models import Person
from genreapp.models import Genre
from django.db.models import Count


@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class HomepageCreateView(CreateView):
    model = Homepage
    form_class = HomepageCreationForm
    template_name = 'homepageapp/create.html'
        
    def form_valid(self, form):
        temp_homepage = form.save(commit=False)
        temp_homepage.writer = self.request.user
        temp_homepage.save()

        # ManyToManyField 처리
        form.save_m2m()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('homepageapp:detail', kwargs={'pk':self.object.pk})
    
class HomepageDetailView(DetailView):
    model = Homepage
    template_name ='homepageapp/detail.html'
    context_object_name = 'homepage'
    
    def get_context_data(self, **kwargs):
        # 기본 컨텍스트를 가져옵니다.
        context = super().get_context_data(**kwargs)
        # 현재 페이지의 객체를 가져옵니다.
        homepage = self.get_object()
        # Homepage와 연결된 모든 Article 객체들을 컨텍스트에 추가합니다.
        context['articles'] = Article.objects.order_by('-created_at')[:10]
        context['artists'] = homepage.artist.all()
        context['persons'] = homepage.person.all()
        context['projects'] = homepage.project.all()
        
        return context

class HomepageView(TemplateView):
    template_name = 'homepageapp/homepage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = Article.objects.annotate(
            sort_date=Coalesce('datetime', 'date')
        ).filter(sort_date__gte=timezone.now(), hide=False).order_by('sort_date')[:4]
        context['popular_artists'] = Artist.objects.filter(hide=False).order_by('-like')[:6]
        context['popular_projects'] = Project.objects.filter(hide=False).order_by('-like')[:6]
        context['latest_communities'] = Community.objects.filter(hide=False).order_by('-created_at')[:10]
        context['latest_persons'] = Person.objects.filter(hide=False).order_by('-updated_at')[:5]
        context['latest_genres'] = Genre.objects.filter(hide=False).order_by('-updated_at')[:5]
        context['hot_artists'] = Artist.objects.filter(hide=False).order_by('-hot_point', '-like')[:10]
        
        return context