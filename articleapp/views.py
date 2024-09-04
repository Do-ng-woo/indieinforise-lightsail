from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from articleapp.decorators import article_ownership_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic.edit import FormMixin

from commentapp.forms import CommentCreationForm
from articleapp.forms import ArticleCreationForm
from articleapp.forms import ArticleSearchForm

from articleapp.models import Article, ArticleUpdateLog
from artistapp.models import Artist
from communityapp.models import Community
from django.urls import reverse, reverse_lazy

from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

import calendar
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from .models import Article
from django.core.serializers import serialize

from django.db.models import Count, DateField
from django.db.models.functions import TruncDate
# views.py에 CalendarDetailView 추가
from django.views.generic import TemplateView

from collections import defaultdict
from django.http import HttpResponse
from django.template.loader import render_to_string


from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.db.models import Case, When, Value, CharField
from django.db.models.functions import Coalesce
#comment 범용
from commentapp.models import Comment 
from django.contrib.contenttypes.models import ContentType


from collections import Counter

from django.db.models import Prefetch

# from django.db import transaction
# from sentence_transformers import SentenceTransformer

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleCreationForm
    template_name = 'articleapp/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 1:
            return HttpResponseForbidden("You do not have permission to create an article.")
        
        temp_article = form.save(commit=False)
        temp_article.writer = self.request.user
        
        if 'save_draft' in self.request.POST:
            temp_article.hide = True
        else:
            temp_article.hide = False
            # 게시글이 완전히 작성된 경우에만 포인트 증가
            profile = self.request.user
            profile.points += 10  # 게시글 작성 시 10 포인트 증가
            if profile.points >= 100:
                profile.level += 1  # 100 포인트마다 레벨 1 증가
                profile.points -= 100  # 레벨 업 후 포인트 초기화
            profile.save()
        
        temp_article.save()
        form.save_m2m()  # ManyToMany 필드를 저장

        # ManyToMany 필드가 저장된 후에 임베딩을 생성
        # transaction.on_commit(lambda: generate_and_save_embeddings(temp_article))
        

        # 수정된 전체 내용을 문자열로 저장합니다.
        update_description = []
        for field in form.fields:
            if field != 'image':  # 이미지 필드 제외
                field_value = form.cleaned_data.get(field, 'N/A')
                if isinstance(field_value, (list, QuerySet)):
                    field_value = ', '.join(str(item) for item in field_value)
                update_description.append(f"{field}: {field_value}")
        update_description_str = "; ".join(update_description)

        # ArticleUpdateLog 객체를 생성하여 생성 정보를 기록합니다.
        ArticleUpdateLog.objects.create(
            article=temp_article,
            updated_by=self.request.user,
            update_description=update_description_str
        )

        return super().form_valid(form)

    

    
    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 1:
            messages.warning(request, "공연정보를 작성할 등급이 안됩니다")
            return redirect('articleapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('articleapp:detail', kwargs={'pk': self.object.pk})
    
    

class ArticleDetailView(DetailView, FormMixin):
    model = Article
    form_class = CommentCreationForm
    context_object_name = 'target_article'
    template_name = 'articleapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        article = self.object
        article.views += 1  # 조회수 1 증가
        article.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        sort = self.request.GET.get('sort')
        tagged_communities = article.community.all()

        # 페이징 처리
        paginator = Paginator(tagged_communities, 10)  # 여기서 self.paginate_by는 페이지당 몇 개의 항목을 보여줄지 결정합니다.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 페이징 처리된 커뮤니티 목록과 페이지 객체를 컨텍스트에 추가
        context['tagged_communities'] = page_obj  # page_obj는 현재 페이지의 객체 목록입니다.
        context['page_obj'] = page_obj  # 페이지 네비게이션을 위해 page_obj도 전달합니다.
        
        # Community 페이지네이션
        community_articles = Community.objects.filter(article=article).order_by('-created_at')
        community_page = self.request.GET.get('community_page', 1)
        community_paginator = Paginator(community_articles, 5)  # 페이지당 10개의 객체
        context['community_articles'] = community_paginator.get_page(community_page)
        
        
         # ContentType을 사용하여 Article 객체에 대한 댓글 필터링
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
        paginator = Paginator(comments, 2)  # 페이지 당 보여줄 댓글 수
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
    
        

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleCreationForm
    context_object_name = 'target_article'
    template_name = 'articleapp/update.html'

    def dispatch(self, request, *args, **kwargs):
        referer_url = request.META.get('HTTP_REFERER')
        article = self.get_object()

        if request.user.level < 1:
            messages.error(request, "You do not have permission to edit this article.")
            return redirect(referer_url if referer_url else '/')

        now = timezone.now()
        if not article.hide:
            # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 같은 게시물 수정한 로그의 수를 카운트
            recent_logs_count = ArticleUpdateLog.objects.filter(
                updated_by=request.user,
                updated_at__gte=now - timedelta(minutes=10),
                hide=False  # hide 상태 확인
            ).count()

            # 10분 이내에 3회 이상 수정 시도를 확인하고 차단
            if recent_logs_count >= 3:
                messages.error(request, "You have reached the edit limit for the last 10 minutes.")
                return redirect(referer_url if referer_url else '/')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        temp_article = form.save(commit=False)
        was_hidden = temp_article.hide

        if 'save_draft' in self.request.POST:
            temp_article.hide = True
        elif 'publish' in self.request.POST:
            temp_article.hide = False
            if was_hidden:
                # 게시글이 완전히 작성된 경우에만 포인트 증가
                profile = self.request.user
                profile.points += 10  # 게시글 작성 시 10 포인트 증가
                if profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 초기화
                profile.save()
        elif not temp_article.hide:  # 일반적인 업데이트
            profile = self.request.user
            profile.points += 3  # 게시글 수정 시 3 포인트 증가
            if profile.points >= 100:
                profile.level += 1  # 100 포인트마다 레벨 1 증가
                profile.points -= 100  # 레벨 업 후 포인트 초기화
            profile.save()

        temp_article.save()
        
        form.save_m2m()  # ManyToMany 필드를 저장

        # ManyToMany 필드가 저장된 후에 임베딩을 생성
        # transaction.on_commit(lambda: generate_and_save_embeddings(temp_article))

        # 수정된 전체 내용을 문자열로 저장합니다.
        update_description = []
        for field in form.fields:
            if field != 'image':  # 이미지 필드 제외
                field_value = form.cleaned_data.get(field, 'N/A')
                if isinstance(field_value, (list, QuerySet)):  # ManyToManyField 처리
                    field_value = ', '.join(str(item) for item in field_value)
                update_description.append(f"{field}: {field_value}")
        update_description_str = "; ".join(update_description)

        # ArticleUpdateLog 객체를 생성하여 수정 정보를 기록합니다.
        ArticleUpdateLog.objects.create(
            article=self.object,
            updated_by=self.request.user,
            update_description=update_description_str,
            hide=temp_article.hide  # hide 상태 기록
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('articleapp:detail', kwargs={'pk': self.object.pk})
    

@method_decorator(article_ownership_required, 'get')
@method_decorator(article_ownership_required, 'post')
class ArticleDeleteView(DeleteView):
    model = Article
    context_object_name= 'target_article'
    success_url = reverse_lazy('articleapp:list')
    template_name = 'articleapp/delete.html' 

from django.db.models import Q
from datetime import datetime

class ArticleListView(ListView):
    model = Article
    context_object_name = 'article_list'
    template_name = 'articleapp/list.html'
    paginate_by = 15
    
    def get_queryset(self):
        
        queryset = Article.objects.filter(hide=False)
        search_keyword = self.request.GET.get('search_keyword', '')
        search_field = self.request.GET.get('search_field', '')
        date_range = self.request.GET.get('date_range', '')

        if search_field == 'title' and search_keyword:
            queryset = queryset.filter(title__icontains=search_keyword)
        elif search_field == 'date':
            if date_range and ' ~ ' in date_range:
                # 날짜 범위를 '-'로 분리
                start_date_str, end_date_str = date_range.split(' ~ ')
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                # date 및 datetime 필드에서 날짜 범위로 검색
                queryset = queryset.filter(
                    Q(date__range=(start_date, end_date)) |
                    Q(datetime__date__range=(start_date, end_date))
                )
            elif search_keyword:
                # 날짜 검색어가 있을 경우 이전 로직 유지
                queryset = queryset.filter(
                    Q(date__icontains=search_keyword) |
                    Q(datetime__date__icontains=search_keyword)
                )
        elif search_field == 'project' and search_keyword:
            queryset = queryset.filter(project__title__icontains=search_keyword)
        elif search_field == 'artist' and search_keyword:
            queryset = queryset.filter(artist__title__icontains=search_keyword)
        elif search_field == 'person' and search_keyword:
            queryset = queryset.filter(person__title__icontains=search_keyword)
            
        # 공연 타입에 따른 필터링 조건 추가
        # 공연 타입에 따른 필터링 조건 및 정렬 로직 추가
        type = self.request.GET.get('type', '')
        if type == 'upcoming':
            queryset = queryset.annotate(
                sort_date=Coalesce('datetime', 'date')
            ).filter(sort_date__gte=timezone.now()).order_by('sort_date')
        elif type == 'past':
            queryset = queryset.annotate(
                sort_date=Coalesce('datetime', 'date')
            ).filter(sort_date__lt=timezone.now()).order_by('-sort_date')
        elif type == 'new':  # 기본 상태 - 최신 작성순으로 정렬
            queryset = queryset.order_by('-created_at')
        else:  # 기본 상태 - 최신 작성순으로 정렬
            queryset = queryset.order_by('-created_at')
        

        return queryset

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET or None)
        context['search_field'] = self.request.GET.get('search_field', 'title')  # 검색 필드 추가
        return context

    
class ArticleEventsAPIView(View):
    def get(self, request, *args, **kwargs):
        # 아티스트 정보와 함께 이벤트를 미리 가져오기
        events = Article.objects.prefetch_related(
            Prefetch('artist', queryset=Artist.objects.order_by('-like'))
        )

        artist_info_by_date = defaultdict(list)
        for event in events:
            event_date = event.datetime.strftime("%Y-%m-%d") if event.datetime else event.date.strftime("%Y-%m-%d")
            for artist in event.artist.all():
                artist_info_by_date[event_date].append((artist.title, artist.like))

        # 각 날짜별로 좋아요가 많은 상위 5개의 아티스트를 선택하고, 5개를 초과하는지 확인
        top_artists_by_date = {}
        for date, artists in artist_info_by_date.items():
            sorted_artists = sorted(artists, key=lambda x: x[1], reverse=True)
            top_artists = [name for name, _ in sorted_artists[:4]]
            if len(sorted_artists) > 4:  # 아티스트 수가 5개를 초과하면 '...' 추가
                top_artists.append('더보기...')
            top_artists_by_date[date] = top_artists

        # 날짜별 이벤트 데이터를 생성
        events_count = [
            {
                'title': "<br>".join(top_artists_by_date[date]),
                'start': date,
                'url': f"/articles/calendar/?date={date}"
            } for date in top_artists_by_date
        ]

        return JsonResponse(events_count, safe=False)

class CalendarDetailAPIView(View):
    def get(self, request, *args, **kwargs):
        date_query = request.GET.get('date')
        events = []
        if date_query:
            date = datetime.strptime(date_query, "%Y-%m-%d").date()
            # datetime 필드의 날짜 부분과 date 필드 모두에서 해당 date와 일치하는 이벤트를 조회합니다.
            events = Article.objects.filter(
                date=date
            ) | Article.objects.filter(
                datetime__date=date  # datetime 필드에서 날짜 부분만 비교
            )

        html = render_to_string('articleapp/calendar_detail.html', {'events': events})
        return HttpResponse(html)
    
def article_update_log_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    update_logs = ArticleUpdateLog.objects.filter(article=article).order_by('-updated_at')
    
    context = {
        'article': article,
        'update_logs': update_logs,
    }
    return render(request, 'articleapp/article_update_logs.html', context)



# 임베딩 모델 로드 (캐시된 모델 사용)
# model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS', cache_folder='./embading/models')

# def generate_and_save_embeddings(article):
#     """
#     Given an Article instance, generate embeddings for the title, content, and combined text,
#     and save them to the instance.
#     """
#     combined_text = article.get_combined_text()
#     print("Combined Text:", combined_text)  # combined_text 출력

#     title_embedding = model.encode(article.title).tobytes()
#     content_embedding = model.encode(article.content).tobytes()
#     combined_text_embedding = model.encode(combined_text).tobytes()
    
#     article.title_embedding = title_embedding
#     article.content_embedding = content_embedding
#     article.combined_text_embedding = combined_text_embedding

#     print("Title Embedding:완료")
#     print("Content Embedding:완료")
#     print("Combined Text Embedding:완료")
    
#     article.save(update_fields=['title_embedding', 'content_embedding', 'combined_text_embedding'])