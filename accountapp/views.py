from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.list import MultipleObjectMixin


from accountapp.decorators import account_ownership_required
from accountapp.models import HelloWorld
from articleapp.models import Article
from communityapp.models import Community
from artistapp.models import Artist
from personapp.models import Person
from projectapp.models import Project
from singapp.models import Sing
from genreapp.models import Genre
from albumapp.models import Album
from instrumentapp.models import Instrument
from commentapp.models import Comment
from likeapp.models import LikeRecord,CommunityLikeRecord, ArtistLikeRecord, PersonLikeRecord, ProjectLikeRecord, SingLikeRecord, GenreLikeRecord, AlbumLikeRecord
from accountapp.forms import FavoriteSearchForm, CustomUserCreationForm, CustomUserUpdateForm
from accountapp.models import FavoriteSearch
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, DeleteView

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError

User = get_user_model()


has_ownership=[account_ownership_required, login_required]
@login_required
def hello_world(request):    
    
    if request.method == "POST":

        temp = request.POST.get('hello_world_input')

        new_hello_world = HelloWorld()
        new_hello_world.text = temp
        new_hello_world.save()

        hello_world_list = HelloWorld.objects.all()
        return HttpResponseRedirect(reverse('accountapp:hello_world'))
    else:
        hello_world_list = HelloWorld.objects.all()
        return render(request, 'accountapp/hello_world.html', context={'hello_world_list': hello_world_list})

        
    
class AccountCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('articleapp:list')
    template_name = 'accountapp/create.html'

    def dispatch(self, request, *args, **kwargs):
        # 사용자가 로그인 상태인지 확인
        if request.user.is_authenticated:
            # 로그인되어 있으면 메인 페이지로 리다이렉트
            return redirect('homepageapp:main')  # 원하는 URL로 리다이렉트
        # 로그인되어 있지 않으면 원래대로 dispatch 진행
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)
    
@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountUpdateView(UpdateView):
    model = User
    context_object_name = 'target_user'
    form_class = CustomUserUpdateForm
    template_name = 'accountapp/update.html'
    success_url = reverse_lazy('articleapp:list')

    def form_valid(self, form):
        return super().form_valid(form)
    
    
class AccountDetailView(DetailView):
    model = User
    context_object_name = 'target_user'
    template_name = 'accountapp/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        view_type = self.request.GET.get('view_type', 'posts')  # 기본값은 'posts'
        content_type = self.request.GET.get('content_type', 'artist')  # 기본값은 'artist'

        content_type_labels = self.get_content_type_labels()
        detail_url_map = self.get_detail_url_map()
        detail_url = detail_url_map.get(content_type, 'communityapp:detail')

        objects = self.get_filtered_objects(view_type, content_type, user)

        # 댓글 수 카운트 및 전체 포스트 수 카운트
        total_posts_count = self.get_total_posts_count(user)
        comments_count = Comment.objects.filter(writer=user).count()

        # 페이지네이션 처리
        page = self.request.GET.get('page', 1)
        paginator = Paginator(objects, 12)
        context['objects'] = paginator.get_page(page)
        context['view_type'] = view_type
        context['content_type'] = content_type
        context['content_type_label'] = content_type_labels.get(content_type, content_type)
        context['total_posts_count'] = total_posts_count
        context['comments_count'] = comments_count
        context['detail_url'] = detail_url

        return context

    def get_content_type_labels(self):
        return {
            'artist': '아티스트',
            'article': '공연',
            'person': '인물',
            'project': '공연장',
            'sing': '노래',
            'album': '앨범',
            'genre': '장르',
            'community': '커뮤니티'
        }

    def get_detail_url_map(self):
        return {
            'artist': 'artistapp:detail',
            'article': 'articleapp:detail',
            'person': 'personapp:detail',
            'project': 'projectapp:detail',
            'sing': 'singapp:detail',
            'album': 'albumapp:detail',
            'genre': 'genreapp:detail',
            'community': 'communityapp:detail'
        }

    def get_filtered_objects(self, view_type, content_type, user):
        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        
        if view_type == 'posts':
            return model.objects.filter(writer=user, hide=False)
        elif view_type == 'drafts':
            return model.objects.filter(writer=user, hide=True)
        elif view_type == 'comments':
            return self.get_commented_objects(content_type, user)
        elif view_type == 'likes':
            return self.get_liked_objects(content_type, user)
        return model.objects.none()

    def get_commented_objects(self, content_type, user):
        comments = Comment.objects.filter(writer=user)
        content_type_ids = {}
        for comment in comments:
            ct = ContentType.objects.get_for_id(comment.content_type_id)
            if ct.model in content_type_ids:
                content_type_ids[ct.model].append(comment.object_id)
            else:
                content_type_ids[ct.model] = [comment.object_id]

        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        return model.objects.filter(pk__in=content_type_ids.get(content_type, []))

    def get_liked_objects(self, content_type, user):
        like_record_map = {
            'artist': ArtistLikeRecord,
            'article': LikeRecord,
            'person': PersonLikeRecord,
            'project': ProjectLikeRecord,
            'sing': SingLikeRecord,
            'album': AlbumLikeRecord,
            'genre': GenreLikeRecord,
            'community': CommunityLikeRecord
        }
        like_record = like_record_map.get(content_type, CommunityLikeRecord)
        liked_ids = like_record.objects.filter(user=user).values_list(content_type, flat=True)
        
        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        return model.objects.filter(pk__in=liked_ids).distinct()

    def get_total_posts_count(self, user):
        return Artist.objects.filter(writer=user).count() + \
               Article.objects.filter(writer=user).count() + \
               Project.objects.filter(writer=user).count() + \
               Person.objects.filter(writer=user).count() + \
               Community.objects.filter(writer=user).count() + \
               Sing.objects.filter(writer=user).count() + \
               Album.objects.filter(writer=user).count() + \
               Genre.objects.filter(writer=user).count()


    


@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountDeleteView(DeleteView):
    model = User
    context_object_name = 'target_user'
    success_url = reverse_lazy('accountapp:login')
    template_name = 'accountapp/delete.html'
    

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accountapp/login.html'

    def dispatch(self, request, *args, **kwargs):
        # 사용자가 로그인 상태인지 확인
        if request.user.is_authenticated:
            # 로그인되어 있으면 메인 페이지로 리다이렉트
            return redirect('homepageapp:main')  # 원하는 URL로 리다이렉트
        # 로그인되어 있지 않으면 원래대로 dispatch 진행
        return super().dispatch(request, *args, **kwargs)
    
    
# ======================================================================================
def add_favorite_search(request):
    if request.method == 'POST':
        form = FavoriteSearchForm(request.POST, user=request.user)
        if form.is_valid():
            favorite_search = form.save(commit=False)
            favorite_search.user = request.user
            existing_count = FavoriteSearch.objects.filter(user=request.user).count()
            if existing_count < 8:
                try:
                    favorite_search.save()
                    messages.success(request, "즐겨찾는 키워드가 추가되었습니다")
                    return redirect(reverse('communityapp:list'))
                except IntegrityError:
                    messages.warning(request, "이미 같은 즐겨찾기 키워드가 존재합니다.")
            else:
                messages.warning(request, "더이상 추가할 수 없습니다. 수정 후 추가를 진행해주세요.")
        else:
            # 특정 에러 메시지를 폼에서 가져와서 메시지로 추가
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.warning(request, error)
            else:
                messages.warning(request, "입력 값이 유효하지 않습니다. 다시 시도해주세요.")
    else:
        form = FavoriteSearchForm(user=request.user)

    return redirect(reverse('communityapp:list'))

def delete_favorite_keyword(request, keyword_id):
    keyword = FavoriteSearch.objects.get(id=keyword_id, user=request.user)
    keyword.delete()
    messages.success(request, "즐겨찾는 키워드가 삭제되었습니다.")
    return redirect(reverse('communityapp:list'))

def get_field_data(request):
    field = request.GET.get('field')
    data = []
    
    if field == 'artist':
        data = list(Artist.objects.filter(hide=False).values('id', 'title'))
    elif field == 'project':
        data = list(Project.objects.filter(hide=False).values('id', 'title'))
    elif field == 'person':
        data = list(Person.objects.filter(hide=False).values('id', 'title'))
    elif field == 'article':
        data = list(Article.objects.filter(hide=False).values('id', 'title'))
    elif field == 'sing':
        data = list(Sing.objects.filter(hide=False).values('id', 'title'))
    elif field == 'album':
        data = list(Album.objects.filter(hide=False).values('id', 'title'))
    elif field == 'genre':
        data = list(Genre.objects.filter(hide=False).values('id', 'title'))
    elif field == 'instrument':
        data = list(Instrument.objects.filter(hide=False).values('id', 'title'))

    return JsonResponse(data, safe=False)