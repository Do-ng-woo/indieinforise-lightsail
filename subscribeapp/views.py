from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, ListView, TemplateView
from django.shortcuts import get_object_or_404

from subscribeapp.models import P_Subscription, A_Subscription, Per_Subscription
from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article



@method_decorator(login_required,'get')
class P_SubscriptionView(RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('projectapp:detail', kwargs={'pk':self.request.GET.get('project_pk')})
    
    def get(self,request,*args,**kwargs):
        project = get_object_or_404(Project, pk=self.request.GET.get('project_pk'))
        user = self.request.user
        subscription = P_Subscription.objects.filter(user=user, project=project)
        
        if subscription.exists():
            subscription.delete()
        else:
            P_Subscription(user=user,project=project).save()
        return super(P_SubscriptionView,self).get(request, *args, **kwargs)

@method_decorator(login_required,'get')
class P_SubscriptionListView(ListView):
    model = Article
    context_object_name = 'article_list'
    template_name = 'subscribeapp/P_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        projects = P_Subscription.objects.filter(user=self.request.user).values_list('project')
        article_list = Article.objects.filter(project__in=projects)
        return article_list
    

@method_decorator(login_required,'get')
class A_SubscriptionView(RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('artistapp:detail', kwargs={'pk':self.request.GET.get('artist_pk')})
    
    def get(self,request,*args,**kwargs):
        artist = get_object_or_404(Artist, pk=self.request.GET.get('artist_pk'))
        user = self.request.user
        subscription = A_Subscription.objects.filter(user=user, artist=artist)
        
        if subscription.exists():
            subscription.delete()
        else:
            A_Subscription(user=user,artist=artist).save()
        return super(A_SubscriptionView,self).get(request, *args, **kwargs)

@method_decorator(login_required,'get')
class A_SubscriptionListView(ListView):
    model = Article
    context_object_name = 'article_list'
    template_name = 'subscribeapp/A_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        artists = A_Subscription.objects.filter(user=self.request.user).values_list('artist')
        article_list = Article.objects.filter(artist__in=artists)
        return article_list
    
@method_decorator(login_required,'get')
class Per_SubscriptionView(RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('personapp:detail', kwargs={'pk':self.request.GET.get('person_pk')})
    
    def get(self,request,*args,**kwargs):
        person = get_object_or_404(Person, pk=self.request.GET.get('person_pk'))
        user = self.request.user
        subscription = Per_Subscription.objects.filter(user=user, person=person)
        
        if subscription.exists():
            subscription.delete()
        else:
            Per_Subscription(user=user,person=person).save()
        return super(Per_SubscriptionView,self).get(request, *args, **kwargs)

@method_decorator(login_required,'get')
class Per_SubscriptionListView(ListView):
    model = Person
    context_object_name = 'person_list'
    template_name = 'subscribeapp/Per_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        persons = Per_Subscription.objects.filter(user=self.request.user).values_list('person')
        article_list = Article.objects.filter(person__in=persons)
        return article_list
    
@method_decorator(login_required, 'get')
class CombinedSubscriptionListView(ListView):
    model = Article
    context_object_name = 'article_list'
    template_name = 'subscribeapp/C_list.html'  # 여기에 통합 템플릿 이름을 업데이트하세요
    paginate_by = 25

    def get_queryset(self):
        # 사용자가 구독한 프로젝트와 아티스트 가져오기
        subscribed_projects = P_Subscription.objects.filter(user=self.request.user).values_list('project', flat=True)
        subscribed_artists = A_Subscription.objects.filter(user=self.request.user).values_list('artist', flat=True)
        subscribed_persons = Per_Subscription.objects.filter(user=self.request.user).values_list('person', flat=True)

        # 구독한 프로젝트와 아티스트에 관련된 글들 가져오기
        article_list = Article.objects.filter(
            Q(project__in=subscribed_projects) | Q(artist__in=subscribed_artists) | Q(person__in=subscribed_persons)
        ).distinct()  # 중복 항목을 피하기 위해 distinct() 사용
        return article_list

@method_decorator(login_required, 'get')
class Artist_SubscriptionListView(ListView):
    model = Artist  # 이제 Artist 객체를 리스트업합니다.
    context_object_name = 'artist_list'  # context 이름을 article_list에서 artist_list로 변경
    template_name = 'subscribeapp/artist_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        # 사용자가 구독한 Artist의 ID 목록을 가져옵니다.
        subscribed_artist_ids = A_Subscription.objects.filter(user=self.request.user).values_list('artist', flat=True)
        # 해당 ID를 기반으로 Artist 객체를 조회합니다.
        artist_list = Artist.objects.filter(id__in=subscribed_artist_ids)
        return artist_list

@method_decorator(login_required, 'get')
class Project_SubscriptionListView(ListView):
    model = Project  # 이제 Project 객체를 리스트업합니다.
    context_object_name = 'project_list'  # context 이름을 article_list에서 project_list로 변경
    template_name = 'subscribeapp/project_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        # 사용자가 구독한 Project의 ID 목록을 가져옵니다.
        subscribed_project_ids = P_Subscription.objects.filter(user=self.request.user).values_list('project', flat=True)
        # 해당 ID를 기반으로 Project 객체를 조회합니다.
        project_list = Project.objects.filter(id__in=subscribed_project_ids)
        return project_list
    
@method_decorator(login_required, 'get')
class Person_SubscriptionListView(ListView):
    model = Person  # 이제 Project 객체를 리스트업합니다.
    context_object_name = 'person_list'  # context 이름을 article_list에서 project_list로 변경
    template_name = 'subscribeapp/person_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        # 사용자가 구독한 Project의 ID 목록을 가져옵니다.
        subscribed_person_ids = Per_Subscription.objects.filter(user=self.request.user).values_list('person', flat=True)
        # 해당 ID를 기반으로 Project 객체를 조회합니다.
        person_list = Person.objects.filter(id__in=subscribed_person_ids)
        return person_list