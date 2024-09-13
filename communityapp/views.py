from django.db.models import Q
from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from communityapp.decorators import community_ownership_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic.edit import FormMixin

from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument


from commentapp.forms import CommentCreationForm
from communityapp.forms import CommunityCreationForm
from communityapp.forms import CommunitySearchForm
from accountapp.models import FavoriteSearch
from accountapp.forms import FavoriteSearchForm

from communityapp.models import Community
from django.urls import reverse, reverse_lazy

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

from django.db import transaction
from django.shortcuts import redirect, resolve_url

from commentapp.models import Comment 
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.core.paginator import Paginator

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class CommunityCreateView(CreateView):
    model = Community
    form_class = CommunityCreationForm
    template_name = 'communityapp/create.html'
    
    
    def form_valid(self,form):
        temp_community = form.save(commit=False)
        temp_community.writer = self.request.user
        temp_community.save()
        
        # 포인트 증가 및 레벨 업 로직
        profile = self.request.user
        profile.points += 10  # 프로젝트 생성 시 10 포인트 증가
        while profile.points >= 100:
            profile.level += 1  # 100 포인트마다 레벨 1 증가
            profile.points -= 100  # 레벨 업 후 포인트 조정
        profile.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('communityapp:detail', kwargs={'pk':self.object.pk})
    
    

class CommunityDetailView(DetailView, SingleObjectMixin, FormMixin):
    model = Community
    form_class = CommentCreationForm
    context_object_name = 'target_community'
    template_name = 'communityapp/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 댓글 수를 별도로 계산할 필요가 없으므로, 이 부분은 제거됩니다.
        
        #################### ContentType을 사용하여 Article 객체에 대한 댓글 필터링
        content_type = ContentType.objects.get_for_model(self.object)
        comments = Comment.objects.filter(content_type=content_type, object_id=self.object.pk) \
                                  .annotate(likes_count=Count('likes'))
        
        # URL 쿼리에 따라 정렬 방식 결정
        sort = self.request.GET.get('sort')
        if sort == 'likes':
            comments = comments.order_by('-likes_count', '-created_at')
        else:  # 기본 정렬 방식은 최신순
            comments = comments.order_by('-created_at')

        # 페이징 처리
        paginator = Paginator(comments, 10)  # 페이지 당 보여줄 댓글 수
        page_number = self.request.GET.get('page')
        comment_page_obj = paginator.get_page(page_number)

        # 컨텍스트에 추가
        context['comments'] = comment_page_obj
        context['comment_page_obj'] = comment_page_obj
        context['sort'] = sort
        
        # ContentType 정보 추가 (이미 존재함)
        context['content_type_id'] = content_type.id  # id 사용
        context['object_id'] = self.object.pk
        
        return context

    def get(self, request, *args, **kwargs):
        # self.object에 현재 커뮤니티 객체를 할당합니다.
        self.object = self.get_object()
        # 조회수 증가 로직
        community = self.object
        community.views += 1
        community.save(update_fields=['views'])
        # FormMixin과 DetailView의 get 메서드를 적절히 처리하기 위해 context를 생성합니다.
        context = self.get_context_data(object=self.object, form=self.get_form())
        
        
        return self.render_to_response(context)

@method_decorator(community_ownership_required, 'get')
@method_decorator(community_ownership_required, 'post')
class CommunityUpdateView(UpdateView):
    model = Community
    form_class = CommunityCreationForm
    context_object_name= 'target_community'
    template_name = 'communityapp/update.html'
        
    def get_success_url(self):
        return reverse('communityapp:detail', kwargs={'pk':self.object.pk})

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class CommunityDeleteView(DeleteView):
    model = Community
    context_object_name= 'target_community'
    success_url = reverse_lazy('communityapp:list')
    template_name = 'communityapp/delete.html' 
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # 포인트 회수 로직
        with transaction.atomic():
            profile = request.user
            profile.points -= 10  # 프로젝트 삭제 시 10 포인트 감소
            if profile.points < 0:
                profile.level -= 1 
                profile.points += 100
            profile.save()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)

from django.db.models import Q
from datetime import datetime

class CommunityListView(ListView):
    model = Community
    context_object_name = 'community_list'
    template_name = 'communityapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Community.objects.filter(hide=False).order_by('-created_at')  # 최신 작성순으로 정렬
        search_keyword = self.request.GET.get('search_keyword', '')
        search_field = self.request.GET.get('search_field', '')
        date_range = self.request.GET.get('date_range', '')
        additional_search_keyword = self.request.GET.get('additional_search_keyword', '')

        if search_field == 'title' and search_keyword:
            queryset = queryset.filter(title__icontains=search_keyword)
        elif search_field == 'date':
            if date_range and ' ~ ' in date_range:
                # 날짜 범위를 '-'로 분리
                start_date_str, end_date_str = date_range.split(' ~ ')
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                # created_at 필드에서 날짜 범위로 검색
                queryset = queryset.filter(created_at__range=(start_date, end_date))
            elif search_keyword:
                # 날짜 검색어가 있을 경우 이전 로직 유지 (이 부분은 created_at 필드로 변경되었습니다)
                queryset = queryset.filter(created_at__icontains=search_keyword)
        elif search_field == 'project' and search_keyword:
            queryset = queryset.filter(project__title__icontains=search_keyword)
        elif search_field == 'artist' and search_keyword:
            queryset = queryset.filter(artist__title__icontains=search_keyword)
        elif search_field == 'person' and search_keyword:
            queryset = queryset.filter(person__title__icontains=search_keyword)
        elif search_field == 'article' and search_keyword:
            queryset = queryset.filter(article__title__icontains=search_keyword)
        elif search_field == 'sing' and search_keyword:
            queryset = queryset.filter(sing__title__icontains=search_keyword)
        elif search_field == 'album' and search_keyword:
            queryset = queryset.filter(album__title__icontains=search_keyword)
        elif search_field == 'genre' and search_keyword:
            queryset = queryset.filter(genre__title__icontains=search_keyword)
        elif search_field == 'instrument' and search_keyword:
            queryset = queryset.filter(instrument__title__icontains=search_keyword)
        
        # 추가 검색 조건 처리
        if additional_search_keyword:
            queryset = queryset.filter(title__icontains=additional_search_keyword)
        
        return queryset

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CommunitySearchForm(self.request.GET or None)
        context['search_field'] = self.request.GET.get('search_field', 'title')  # 검색 필드 추가
        
        context['favorite_search_form'] = FavoriteSearchForm()
        if self.request.user.is_authenticated:
            context['favorite_keywords'] = FavoriteSearch.objects.filter(user=self.request.user)
        else:
            context['favorite_keywords'] = []
            
        # Select2에서 사용할 객체들을 컨텍스트에 추가
        context['artists'] = Artist.objects.all()
        context['projects'] = Project.objects.all()
        context['persons'] = Person.objects.all()
        context['articles'] = Article.objects.all()
        context['sings'] = Sing.objects.all()
        context['albums'] = Album.objects.all()
        context['genres'] = Genre.objects.all()
        context['instruments'] = Instrument.objects.all()
            
        return context
    

@csrf_exempt
def file_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # 파일 저장 로직 (예: MEDIA_ROOT 아래에 저장)
            file_path = os.path.join('uploads', file.name)
            save_path = os.path.join(settings.MEDIA_ROOT, file_path)
            with open(save_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # TinyMCE에 반환할 URL
            file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Failed to upload file.'})
    
