from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from singapp.decorators import sing_ownership_required


from singapp.forms import SingCreationForm, SingUpdateForm, SingSearchForm
from singapp.models import Sing,Subtitle,Description,SingUpdateLog
from articleapp.models import Article
from artistapp.models import Artist
from subscribeapp.models import Per_Subscription

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormMixin
from commentapp.forms import CommentCreationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from communityapp.models import Community

from django.http import HttpResponseForbidden
from django.views.generic import TemplateView

from collections import defaultdict
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import F

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Coalesce
from datetime import datetime


from commentapp.models import Comment 
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class SingCreateView(CreateView):
    model = Sing
    form_class = SingCreationForm
    template_name = 'sing/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 0:
            messages.warning(self.request, "인물정보를 작성할 등급이 안됩니다.")
            return redirect('singapp:list')
        
        with transaction.atomic():
            temp_sing = form.save(commit=False)
            temp_sing.writer = self.request.user

            if 'save_draft' in self.request.POST:
                temp_sing.hide = True
            elif 'publish' in self.request.POST:
                temp_sing.hide = False
                profile = self.request.user
                profile.points += 10  # Sing 생성 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_sing.save()
            # form.save_m2m()을 호출해 Many-to-Many 데이터 저장
            form.save_m2m()

            descriptions = {}
            for key, value in self.request.POST.items():
                if 'detailed_descriptions' in key:
                    index = key.split('[')[1].split(']')[0]
                    field_type = key.split('[')[2].split(']')[0]

                    if index not in descriptions:
                        descriptions[index] = {'name': '', 'text': ''}

                    if field_type == 'name':
                        descriptions[index]['name'] = value
                    elif field_type == 'value':
                        descriptions[index]['text'] = value

            for desc in descriptions.values():
                Description.objects.create(sing=temp_sing, name=desc['name'], text=desc['text'])

            # Sing 생성 로그 기록
            update_description = "Sing created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            SingUpdateLog.objects.create(
                sing=temp_sing,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_sing.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 0:
            messages.warning(request, "인물정보를 작성할 등급이 안됩니다")
            return redirect('singapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('singapp:detail', kwargs={'pk': self.object.pk})

class SingDetailView(DetailView, FormMixin):
    model = Sing
    form_class = CommentCreationForm
    context_object_name = 'target_sing'
    template_name = 'singapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        sing = self.object
        sing.views += 1  # 조회수 1 증가
        sing.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sing = self.object
        user = self.request.user
        today = timezone.now().date()
        

        # Community 페이지네이션
        community_articles = Community.objects.filter(sing=sing).order_by('-created_at')
        community_page = self.request.GET.get('community_page', 1)
        community_paginator = Paginator(community_articles, 5)  # 페이지당 10개의 객체
        context['community_articles'] = community_paginator.get_page(community_page)
        
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
        
        # 케러셀 로직 ------------------
        # Sing 인스턴스에 연결된 모든 Artist 인스턴스를 조회
        related_artists = sing.artist.all()
        context['related_artists'] = related_artists
        
        if related_artists.exists():
            # Q 객체를 사용하여 여러 Artist 조건을 OR로 결합하여 Article 조회
            articles_query = Q()
            for artist in related_artists:
                articles_query |= Q(artist=artist)
            
            articles = Article.objects.filter(articles_query).annotate(
                sort_date=Coalesce('datetime', 'date')
            )
            # 오늘 날짜를 기준으로 과거와 미래 게시글 분리 및 정렬
            past_articles = articles.filter(sort_date__lt=today).order_by('-sort_date')
            future_articles = articles.filter(sort_date__gte=today).order_by('sort_date')
            past_articles_sorted = list(past_articles)[::-1]
            future_articles_sorted = list(future_articles)
            all_articles_sorted = past_articles_sorted + future_articles_sorted
        else:
            all_articles_sorted = []
            past_articles_sorted = []
            future_articles_sorted = []

        context['all_articles'] = all_articles_sorted

        if future_articles_sorted:
            initial_slide_index = len(past_articles_sorted)
        else:
            initial_slide_index = len(past_articles_sorted) - 1 if past_articles_sorted else 0
        context['initial_slide_index'] = initial_slide_index

        return context
    
class SingListView(ListView):
    model = Sing
    context_object_name = 'sing_list'
    template_name = 'singapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(hide=False)
        search_keyword = self.request.GET.get('search_keyword', '')
        search_field = self.request.GET.get('search_field', '')

        if search_field == 'title' and search_keyword:
            # 제목으로 검색
            queryset = queryset.filter(title__icontains=search_keyword)
        elif search_field == 'artist' and search_keyword:
            # 아티스트 이름으로 검색
            queryset = queryset.filter(artist__title__icontains=search_keyword)
        
        # 정렬 기준 추가
        order_by = self.request.GET.get('order_by', 'title')
        if order_by == 'popularity':
            queryset = queryset.annotate(
                weighted_score=F('like') * 0.8 + F('views') * 0.2
            ).order_by('-weighted_score')
        elif order_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # 기본값은 'title'
            queryset = queryset.order_by('title')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SingSearchForm(self.request.GET or None)
        context['search_field'] = self.request.GET.get('search_field', 'title')  # 검색 필드 추가
        return context
    
@method_decorator(sing_ownership_required, 'get')
@method_decorator(sing_ownership_required, 'post')
class SingDeleteView(DeleteView):
    model = Sing
    context_object_name='target_sing'
    success_url = reverse_lazy('singapp:list')
    template_name = 'singapp/delete.html' 
    
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
    
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class SingUpdateView(UpdateView):
    model = Sing
    form_class = SingUpdateForm
    context_object_name = 'target_sing'
    template_name = 'singapp/update.html'
    
    def get(self, request, *args, **kwargs): #subtitle 기존에 입력된것 나타나게 하기
        self.object = self.get_object()
        form = self.get_form()

        # 여기서 기존 데이터를 폼에 채워 넣음
        form.fields['sub_titles_input'].initial = ', '.join(self.object.sub_titles.values_list('name', flat=True))

        return self.render_to_response(self.get_context_data(form=form))
    
    #수정 권한 제한
    def dispatch(self, request, *args, **kwargs):
        referer_url = request.META.get('HTTP_REFERER')
        if request.user.level < 0:
            messages.error(request, "You do not have permission to edit this sing.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 싱 수정한 로그의 수를 카운트
        recent_logs_count = SingUpdateLog.objects.filter(
            updated_by=request.user,
            updated_at__gte=now - timedelta(minutes=10),
            hide=False
        ).count()
        
        # 10분 이내에 3회 이상 수정 시도를 확인하고 차단
        if recent_logs_count >= 3:
            messages.error(request, "You have reached the edit limit for the last 10 minutes.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]
        return context

    def form_valid(self, form):
        with transaction.atomic():
            sing = form.save(commit=False)
            was_hidden = sing.hide

            if 'save_draft' in self.request.POST:
                sing.hide = True
            elif 'publish' in self.request.POST:
                sing.hide = False
                if was_hidden:
                    # 싱이 완전히 게시된 경우에만 포인트 증가
                    profile = self.request.user
                    profile.points += 10  # 싱 게시 시 10 포인트 증가
                    while profile.points >= 100:
                        profile.level += 1  # 100 포인트마다 레벨 1 증가
                        profile.points -= 100  # 레벨 업 후 포인트 조정
                    profile.save()
            elif not sing.hide:  # 일반적인 업데이트
                profile = self.request.user
                profile.points += 3  # 싱 수정 시 3 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            sing.save()

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in sing.detailed_descriptions.all()}
            descriptions_data = {}
            for key, value in self.request.POST.items():
                if 'detailed_descriptions' in key:
                    index = key.split('[')[1].split(']')[0]
                    field_type = key.split('[')[2].split(']')[0]

                    # 데이터 구조 준비
                    if index not in descriptions_data:
                        descriptions_data[index] = {'id': None, 'name': '', 'text': ''}

                    # 데이터 추출
                    if field_type == 'id':
                        descriptions_data[index]['id'] = value
                    elif field_type == 'name':
                        descriptions_data[index]['name'] = value
                    elif field_type == 'value':
                        descriptions_data[index]['text'] = value

            # 데이터 저장 및 업데이트
            for desc in descriptions_data.values():
                description_id = desc.get('id')
                if description_id and int(description_id) in existing_descriptions:
                    # 기존 설명 업데이트
                    existing_description = existing_descriptions[int(description_id)]
                    existing_description.name = desc['name']
                    existing_description.text = desc['text']
                    existing_description.save()
                    del existing_descriptions[int(description_id)]
                else:
                    # 새로운 설명 추가
                    Description.objects.create(sing=sing, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # 싱 수정 로그 기록
            update_description = "싱 정보 업데이트 로그: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    field_value = form.cleaned_data.get(field, 'N/A')
                    # ManyToManyField 처리
                    if isinstance(field_value, (list, QuerySet)):
                        field_value = ', '.join(str(item) for item in field_value)
                    update_description += f"{field}: {field_value}, "
            update_description = update_description.rstrip(', ')
            
            # 현재의 detailed_descriptions을 문자열로 변환하여 로그 메시지에 추가
            detailed_descriptions_str = "; ".join(
                [f"{desc.name}: {desc.text}" for desc in sing.detailed_descriptions.all()]
            )
            update_description += f"\n 추가 입력한 정보: {detailed_descriptions_str}"

            # Sing 수정 로그 기록
            SingUpdateLog.objects.create(
                sing=sing,
                updated_by=self.request.user,
                update_description=update_description,
                hide=sing.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('singapp:detail', kwargs={'pk': self.object.pk})

    
@login_required
@require_POST
def delete_description(request):
    description_id = request.POST.get('id')
    try:
        description = Description.objects.get(id=description_id)
        description.delete()
        return JsonResponse({'status': 'success'}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': '설명이 존재하지 않습니다.'}, status=404)
    

def sing_update_log_view(request, pk):
    sing = get_object_or_404(Sing, pk=pk)
    update_logs = SingUpdateLog.objects.filter(sing=sing).order_by('-updated_at')
    
    context = {
        'sing': sing,
        'update_logs': update_logs,
    }
    return render(request, 'singapp/sing_update_logs.html', context)

