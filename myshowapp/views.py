
from articleapp.models import Article
# from sentence_transformers import SentenceTransformer, util
import numpy as np
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from articleapp.models import Article

from myshowapp.models import UserPerformance, Stamp
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from django.db.models import F, Value
from django.db.models.functions import Coalesce
import json
from django.core.serializers.json import DjangoJSONEncoder

from myshowapp.utils import create_stamp_image, split_text, convert_image, draw_arc_text
import random
from django.contrib import messages

from myshowapp.models import MyShow_illust, Background_illust, Singer_illust, Guitarist_illust, Bassist_illust, Drummer_illust, Keyboardist_illust, Audience_illust, Lighting_illust
from myshowapp.forms import MyShow_illust_Form
from django.views.generic.edit import FormView

from accountapp.models import CustomUser

from django.http import Http404

from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Case, When, IntegerField, Value
from django.db.models.functions import Replace

class UserPerformanceCreateView(CreateView):
    model = UserPerformance
    fields = ['memo', 'running_time']  # 상태와 평점은 폼에서 숨겨진 필드로 처리
    template_name = 'myshowapp/search_detail.html'
    success_url = reverse_lazy('myshowapp:card_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.article = get_object_or_404(Article, pk=self.kwargs['pk'])
        form.instance.status = self.request.POST.get('status')
        form.instance.rating = self.request.POST.get('rating')

        response = super().form_valid(form)

        # 스탬프 생성 및 업데이트
        stamp, stamp_image = create_stamp(form.instance.article, self.request.user)
        form.instance.stamp = stamp
        form.instance.stamp_image = stamp_image
        form.instance.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_article'] = get_object_or_404(Article, pk=self.kwargs['pk'])
        return context
    


class UserPerformanceListView(LoginRequiredMixin, ListView):
    model = UserPerformance
    template_name = 'myshowapp/card_list.html'
    context_object_name = 'performance_list'

    def get_queryset(self):
        # 현재 로그인한 사용자의 UserPerformance만 필터링하여 정렬
        return UserPerformance.objects.filter(user=self.request.user).annotate(
            sort_date=Coalesce('article__datetime', 'article__date')
        ).order_by('-sort_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myshow_exists'] = MyShow_illust.objects.filter(user=self.request.user).exists()
        return context


class UserPerformanceStampListView(LoginRequiredMixin, ListView):
    model = UserPerformance
    template_name = 'myshowapp/stamp_list.html'
    context_object_name = 'performance_list'

    def get_queryset(self):
        # 현재 로그인한 사용자의 UserPerformance만 필터링하여 정렬
        return UserPerformance.objects.filter(user=self.request.user).annotate(
            sort_date=Coalesce('article__datetime', 'article__date')
        ).order_by('-sort_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myshow_exists'] = MyShow_illust.objects.filter(user=self.request.user).exists()
        return context

    
class UserPerformanceUpdateView(LoginRequiredMixin, UpdateView):
    model = UserPerformance
    fields = ['status', 'rating', 'memo']
    template_name = 'myshowapp/myshow_detail.html'
    context_object_name = 'performance'

    def get_object(self, queryset=None):
        return get_object_or_404(UserPerformance, pk=self.kwargs['pk'], user=self.request.user)
    
    def get_success_url(self):
        return reverse('myshowapp:userperformance_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance = self.get_object()
        context['performance'] = performance
        context['stamp'] = performance.stamp
        return context

class UserPerformanceDeleteView(LoginRequiredMixin, DeleteView):
    model = UserPerformance
    template_name = 'myshowapp/delete.html'
    success_url = reverse_lazy('myshowapp:card_list')
    

class StampUpdateView(UpdateView):
    model = Stamp
    fields = ['font_choice', 'background_choice', 'center_image_choice', 'color_choice', 'first_line', 'second_line', 'third_line']
    template_name = 'myshowapp/stamp_update.html'
    context_object_name = 'stamp'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stamp = self.get_object()
        user_performance = get_object_or_404(UserPerformance, stamp=stamp)
        context['article'] = stamp.article
        context['full_text'] = stamp.full_text
        context['date'] = stamp.date
        context['user_performance'] = user_performance
        return context

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'randomize':
            self.object.font_choice = random.randint(1, 6)
            self.object.background_choice = random.randint(1, 3)
            self.object.center_image_choice = random.randint(1, 4)
            self.object.color_choice = random.choice(['blue', 'yellow', 'red', 'black'])
        response = super().form_valid(form)
        self.object.stamp_image = create_stamp_image(self.object)
        self.object.save()
        return response
    
    def get_success_url(self):
        return reverse_lazy('myshowapp:stamp_update', kwargs={'pk': self.object.pk})

def search_performances(request):
    query = request.GET.get('q', '').replace(' ', '')  # 입력된 검색어의 공백 제거
    page_number = int(request.GET.get('page', 1))
    results_per_page = 10
    results = []
    page_obj = None

    # 검색어가 한 글자일 경우 메시지를 표시하고 검색하지 않음
    if len(query) < 2:
        context = {'message': '두 글자 이상부터 검색 가능합니다.'}
        return render(request, 'myshowapp/search_result.html', context)

    if query:
        # 현재 날짜 기준 1년 전과 1년 후의 날짜 계산
        current_time = timezone.now()
        one_year_before = current_time - timedelta(days=365)
        one_year_after = current_time + timedelta(days=365)

        # 서브타이틀에서 검색어와 일치하는 Artist 검색
        matching_artists = Artist.objects.filter(
            Q(title__icontains=query) |
            Q(Replace('title', Value(' '), Value(''))__icontains=query) |
            Q(sub_titles__title__icontains=query) |
            Q(Replace('sub_titles__title', Value(' '), Value(''))__icontains=query)
        ).distinct()

        # Artist에 관련된 Article을 필터링하기 위한 ID 목록 생성
        artist_ids = matching_artists.values_list('id', flat=True)

        # 검색 조건 설정 (person 필드 제외)
        search_conditions = (
            Q(title__icontains=query) |
            Q(Replace('title', Value(' '), Value(''))__icontains=query) |
            Q(artist__title__icontains=query) |
            Q(Replace('artist__title', Value(' '), Value(''))__icontains=query) |
            Q(project__title__icontains=query) |
            Q(Replace('project__title', Value(' '), Value(''))__icontains=query) |
            Q(artist__id__in=artist_ids)  # Artist ID를 기반으로 Article 검색
        )

        # 1년 전후의 공연 필터링
        within_one_year = Article.objects.filter(
            search_conditions,
            Q(datetime__range=(one_year_before, one_year_after)) |
            Q(date__range=(one_year_before.date(), one_year_after.date()))
        ).annotate(
            sort_date=Coalesce('datetime', 'date'),
            relevance=Case(
                When(title__icontains=query, then=4),
                When(Replace('title', Value(' '), Value(''))__icontains=query, then=4),
                When(artist__title__icontains=query, then=3),
                When(Replace('artist__title', Value(' '), Value(''))__icontains=query, then=3),
                When(project__title__icontains=query, then=2),
                When(Replace('project__title', Value(' '), Value(''))__icontains=query, then=2),
                default=0,
                output_field=IntegerField()
            )
        ).distinct().order_by('-relevance', '-created_at')

        # 1년을 초과하는 공연 필터링
        beyond_one_year = Article.objects.filter(
            search_conditions
        ).exclude(
            Q(datetime__range=(one_year_before, one_year_after)) |
            Q(date__range=(one_year_before.date(), one_year_after.date()))
        ).annotate(
            sort_date=Coalesce('datetime', 'date'),
            relevance=Case(
                When(title__icontains=query, then=4),
                When(Replace('title', Value(' '), Value(''))__icontains=query, then=4),
                When(artist__title__icontains=query, then=3),
                When(Replace('artist__title', Value(' '), Value(''))__icontains=query, then=3),
                When(project__title__icontains=query, then=2),
                When(Replace('project__title', Value(' '), Value(''))__icontains=query, then=2),
                default=0,
                output_field=IntegerField()
            )
        ).distinct().order_by('-relevance', '-created_at')

        # 두 개의 쿼리셋을 합쳐서 전체 결과 생성
        combined_results = list(within_one_year) + list(beyond_one_year)

        # 페이지네이션 적용
        paginator = Paginator(combined_results, results_per_page)  # 페이지당 10개씩
        page_obj = paginator.get_page(page_number)
        results = page_obj.object_list

    return render(request, 'myshowapp/search_result.html', {'results': results, 'query': query, 'page_obj': page_obj})


# 임베딩 모델 로드
# model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

# def search_performances(request):
#     query = request.GET.get('q')
#     page_number = int(request.GET.get('page', 1))
#     results_per_page = 10
#     results = []
#     page_obj = None

#     if query:
#         # 검색어 임베딩
#         query_embedding = model.encode(query)
        
#         # 모든 임베딩 데이터 로드
#         articles = Article.objects.filter(title_embedding__isnull=False, content_embedding__isnull=False, combined_text_embedding__isnull=False)
#         title_embeddings = []
#         content_embeddings = []
#         combined_text_embeddings = []
#         article_list = []

#         for article in articles:
#             title_embedding = np.frombuffer(article.title_embedding, dtype=np.float32)
#             content_embedding = np.frombuffer(article.content_embedding, dtype=np.float32)
#             combined_text_embedding = np.frombuffer(article.combined_text_embedding, dtype=np.float32)
            
#             title_embeddings.append(title_embedding)
#             content_embeddings.append(content_embedding)
#             combined_text_embeddings.append(combined_text_embedding)
#             article_list.append(article)
        
#         title_embeddings = np.array(title_embeddings)
#         content_embeddings = np.array(content_embeddings)
#         combined_text_embeddings = np.array(combined_text_embeddings)
        
#         # 유사도 계산
#         title_scores = util.pytorch_cos_sim(query_embedding, title_embeddings).cpu().numpy().flatten()
#         content_scores = util.pytorch_cos_sim(query_embedding, content_embeddings).cpu().numpy().flatten()
#         combined_text_scores = util.pytorch_cos_sim(query_embedding, combined_text_embeddings).cpu().numpy().flatten()

#         # 상위 결과 선택
#         top_n = 5
#         top_title_indices = np.argsort(-title_scores)[:top_n]
#         top_combined_text_indices = np.argsort(-combined_text_scores)[:top_n]
#         top_content_indices = np.argsort(-content_scores)[:top_n]

#         # 필터링된 기사 리스트
#         filtered_indices = set(top_title_indices.tolist() + top_combined_text_indices.tolist() + top_content_indices.tolist())
#         filtered_article_list = [article_list[idx] for idx in filtered_indices]
#         filtered_title_scores = title_scores[list(filtered_indices)]
#         filtered_combined_text_scores = combined_text_scores[list(filtered_indices)]
#         filtered_content_scores = content_scores[list(filtered_indices)]

#         # 가중치 적용
#         final_scores = (
#             filtered_title_scores * 1.2 +
#             filtered_combined_text_scores * 1.1 +
#             filtered_content_scores * 1
#         )

#         # 최종 정렬
#         sorted_articles_with_scores = sorted(
#             zip(filtered_article_list, final_scores),
#             key=lambda x: -x[1]
#         )
#         sorted_articles = [article for article, score in sorted_articles_with_scores]

#         # 페이지네이션 적용
#         paginator = Paginator(sorted_articles, results_per_page)  # 페이지당 10개씩
#         page_obj = paginator.get_page(page_number)
#         results = page_obj.object_list

#     return render(request, 'myshowapp/search_result.html', {'results': results, 'query': query, 'page_obj': page_obj})



def create_stamp(article, user):
    full_text = article.title
    first_line, second_line, third_line = split_text(full_text)

    if article.datetime:
        date = article.datetime.date()  # datetime 필드에서 날짜를 가져옴
    else:
        date = article.date  # date 필드에서 날짜를 가져옴
        
    font_choice = random.randint(1, 6)
    background_choice = random.randint(1, 3)
    center_image_choice = random.randint(1, 4)
    color_choice = random.choice(['blue', 'yellow', 'red', 'black'])

    stamp = Stamp.objects.create(
        article=article,
        full_text=full_text,
        first_line=first_line,
        second_line=second_line,
        third_line=third_line,
        date=date,
        font_choice=font_choice,
        background_choice=background_choice,
        center_image_choice=center_image_choice,
        color_choice=color_choice
    )

    stamp_image = create_stamp_image(stamp)
    
    return stamp, stamp_image



class MyShowIllustCreateView(LoginRequiredMixin, CreateView):
    model = MyShow_illust
    form_class = MyShow_illust_Form
    template_name = 'myshowapp/illust_create.html'

    def dispatch(self, request, *args, **kwargs):
        if MyShow_illust.objects.filter(user=self.request.user).exists():
            messages.warning(self.request, "이미 일러스트가 존재합니다. 더이상 생성할 수 없습니다.")
            return redirect('myshowapp:detail_myshow_illust', username=self.request.user.username)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('myshowapp:detail_myshow_illust', kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['singers'] = Singer_illust.objects.all()
        context['guitarists'] = Guitarist_illust.objects.all()
        context['bassists'] = Bassist_illust.objects.all()
        context['drummers'] = Drummer_illust.objects.all()
        context['keyboardists'] = Keyboardist_illust.objects.all()
        context['audiences'] = Audience_illust.objects.all()
        context['lightings'] = Lighting_illust.objects.all()
        context['backgrounds'] = Background_illust.objects.all()
        context['positions'] = {}  # 새로 생성하는 경우 초기 positions 설정
        context['sizes'] = {}  # 새로 생성하는 경우 초기 sizes 설정
        context['z_indices'] = {}  # 새로 생성하는 경우 초기 z_indices 설정
        context['performance_points'] = self.request.user.performance_points
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.positions = self.request.POST.get('positions', '{}')
        form.instance.sizes = self.request.POST.get('sizes', '{}')
        form.instance.z_indices = self.request.POST.get('z_indices', '{}')
        return super().form_valid(form)
    
class MyShowIllustUpdateView(LoginRequiredMixin, UpdateView):
    model = MyShow_illust
    form_class = MyShow_illust_Form
    template_name = 'myshowapp/illust_update.html'
    context_object_name = 'myshow'

    def get_success_url(self):
        return reverse('myshowapp:detail_myshow_illust', kwargs={'username': self.request.user.username})

    def get_object(self):
        return get_object_or_404(MyShow_illust, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['performance_points'] = self.request.user.performance_points
        context['singers'] = Singer_illust.objects.all()
        context['guitarists'] = Guitarist_illust.objects.all()
        context['bassists'] = Bassist_illust.objects.all()
        context['drummers'] = Drummer_illust.objects.all()
        context['keyboardists'] = Keyboardist_illust.objects.all()
        context['audiences'] = Audience_illust.objects.all()
        context['lightings'] = Lighting_illust.objects.all()
        context['backgrounds'] = Background_illust.objects.all()
        context['positions'] = json.loads(self.object.positions or '{}')
        context['sizes'] = json.loads(self.object.sizes or '{}')
        context['z_indices'] = json.loads(self.object.z_indices or '{}')
        
        # 현재 선택된 객체의 ID를 추가
        context['selected_singer'] = self.object.singer.id if self.object.singer else None
        context['selected_guitarist'] = self.object.guitarist.id if self.object.guitarist else None
        context['selected_bassist'] = self.object.bassist.id if self.object.bassist else None
        context['selected_drummer'] = self.object.drummer.id if self.object.drummer else None
        context['selected_keyboardist'] = self.object.keyboardist.id if self.object.keyboardist else None
        context['selected_audience'] = self.object.audience.id if self.object.audience else None
        context['selected_lighting'] = self.object.lighting.id if self.object.lighting else None
        context['selected_background'] = self.object.background.id if self.object.background else None
        
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.positions = self.request.POST.get('positions', '{}')
        form.instance.sizes = self.request.POST.get('sizes', '{}')
        form.instance.z_indices = self.request.POST.get('z_indices', '{}')
        return super().form_valid(form)
    

class MyShowIllustDetailView(DetailView):
    model = MyShow_illust
    template_name = 'myshowapp/illust_detail.html'
    context_object_name = 'myshow'

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            user = get_object_or_404(CustomUser, username=username)
        except Http404:
            return None
        return MyShow_illust.objects.filter(user=user).first()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            messages.warning(request, "아직 사용자가 일러스트를 만들지 않았거나 존재하지 않는 사용자 입니다.")
            return redirect('homepageapp:main')  # 사용자가 없을 때의 리다이렉트 주소
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['positions'] = json.loads(self.object.positions or '{}')
        context['sizes'] = json.loads(self.object.sizes or '{}')
        context['z_indices'] = json.loads(self.object.z_indices or '{}')
        context['user'] = self.object.user
        context['myshow_exists'] = MyShow_illust.objects.filter(user=self.request.user).exists()
        return context
    
    
class StartIllustView(TemplateView):
    template_name = 'myshowapp/illust_start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myshow_exists'] = MyShow_illust.objects.filter(user=self.request.user).exists()
        return context
    
class MyShowIllustDeleteView(LoginRequiredMixin, DeleteView):
    model = MyShow_illust
    success_url = reverse_lazy('myshowapp:start_illust')
    template_name = 'myshowapp/illust_update.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "일러스트가 성공적으로 삭제되었습니다. 새롭게 일러스트 만들기를 시작해 보세요")
        return super().delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(MyShow_illust, user=self.request.user)