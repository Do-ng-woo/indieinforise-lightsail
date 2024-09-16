from django.shortcuts import render
from django.db.models import Q
from django.conf import settings

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from projectapp.decorators import project_ownership_required


from projectapp.forms import ProjectCreationForm, ProjectUpdateForm
from projectapp.models import Project, Description, ProjectUpdateLog
from articleapp.models import Article
from subscribeapp.models import P_Subscription

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from communityapp.models import Community
from django.views.generic.edit import FormMixin
from commentapp.forms import CommentCreationForm

from django.core.serializers import serialize
import json

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from django.db.models import Count, DateField
from django.db.models.functions import TruncDate
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
from django.db import transaction

from django.db.models import Case, When, Value, CharField
from django.db.models.functions import Coalesce

from commentapp.models import Comment 
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models import F

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectCreationForm
    template_name = 'projectapp/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 1:
            messages.warning(self.request, "Stage를 작성할 등급이 안됩니다.")
            return redirect('projectapp:list')
        
        with transaction.atomic():
            temp_project = form.save(commit=False)
            temp_project.writer = self.request.user
            
            if 'save_draft' in self.request.POST:
                temp_project.hide = True
            elif 'publish' in self.request.POST:
                temp_project.hide = False
                profile = self.request.user
                profile.points += 10  # 프로젝트 생성 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_project.save()

            # Description 객체 생성 로직 유지
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
                Description.objects.create(project=temp_project, name=desc['name'], text=desc['text'])

            # 프로젝트 생성 로그 기록
            update_description = "Project created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            ProjectUpdateLog.objects.create(
                project=temp_project,  # 여기서는 project로 변경해야 합니다.
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_project.hide  # hide 상태 기록
            )

        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 1:
            messages.warning(request, "Stage를 작성할 등급이 안됩니다")
            return redirect('projectapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('projectapp:detail', kwargs={'pk': self.object.pk})
    
class ProjectDetailView(DetailView, FormMixin):
    model = Project
    form_class = CommentCreationForm
    context_object_name = 'target_project'
    template_name = 'projectapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        project = self.object
        project.views += 1  # 조회수 1 증가
        project.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        today = timezone.now().date()
        
        # 인증된 사용자에 대한 구독 정보 처리
        if user.is_authenticated:
            context['subscription'] = P_Subscription.objects.filter(user=user, project=project)
        else:
            context['subscription'] = None
        
         # 프로젝트의 위도와 경도를 컨텍스트에 추가
        context['latitude'] = project.latitude
        context['longitude'] = project.longitude

        # 카카오 API 키 추가
        context['kakao_api_key'] = settings.KAKAO_JS_API_KEY

        
        
        # Article 쿼리셋에 sort_date 주석 추가
        articles = Article.objects.filter(project=project, hide=False).annotate(
            sort_date=Coalesce('datetime', 'date')
        )
        # 오늘 날짜를 기준으로 과거와 미래 게시글 분리 및 정렬
        past_articles = articles.filter(sort_date__lt=today).order_by('-sort_date')
        future_articles = articles.filter(sort_date__gte=today).order_by('sort_date')
        # 과거 게시글을 역순으로 정렬하여 가장 최근 과거 게시글이 리스트의 앞에 오도록 함
        past_articles_sorted = list(past_articles)[::-1]
        # 미래 게시글은 이미 가까운 미래 순으로 정렬됨
        future_articles_sorted = list(future_articles)
        # 가장 가까운 미래 게시글이 리스트의 중앙에 오도록 두 리스트 합치기
        all_articles_sorted = past_articles_sorted + future_articles_sorted
        # Swiper의 initialSlide 값을 설정하기 위한 가장 가까운 미래 게시글의 인덱스 찾기
        if future_articles_sorted:
            initial_slide_index = len(past_articles_sorted)
        else:
            initial_slide_index = len(past_articles_sorted) - 1 if past_articles_sorted else 0
        # context에 추가
        context['all_articles'] = all_articles_sorted
        context['initial_slide_index'] = initial_slide_index

        # Community 페이지네이션
        community_articles = Community.objects.filter(project=project).order_by('-created_at')
        community_page = self.request.GET.get('community_page', 1)
        community_paginator = Paginator(community_articles, 5)  # 페이지당 10개의 객체
        context['community_articles'] = community_paginator.get_page(community_page)
        
        context['project_id'] = project.id
        
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
        
        
class ProjectListView(ListView):
    model = Project
    context_object_name = 'project_list'
    template_name = 'projectapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Project.objects.filter(hide=False)

        # 검색어가 있는 경우, 제목에서 검색
        search_keyword = self.request.GET.get('search_keyword', None)
        if search_keyword:
            queryset = queryset.filter(title__icontains=search_keyword)

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
    
@method_decorator(project_ownership_required, 'get')
@method_decorator(project_ownership_required, 'post')
class ProjectDeleteView(DeleteView):
    model = Project
    context_object_name='target_project'
    success_url = reverse_lazy('projectapp:list')
    template_name = 'projectapp/delete.html' 
    
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
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    context_object_name= 'target_project'
    template_name = 'projectapp/update.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]
        return context
    
    def dispatch(self, request, *args, **kwargs):
        referer_url = request.META.get('HTTP_REFERER')
        project = self.get_object()

        if request.user.level < 1:
            messages.error(request, "You do not have permission to edit this project.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 프로젝트 수정한 로그의 수를 카운트
        recent_logs_count = ProjectUpdateLog.objects.filter(
            updated_by=request.user,
            updated_at__gte=now - timedelta(minutes=10),
            hide=False
        ).count()

        # 10분 이내에 3회 이상 수정 시도를 확인하고 차단
        if recent_logs_count >= 3:
            messages.error(request, "You have reached the edit limit for the last 10 minutes.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        with transaction.atomic():
            temp_project = form.save(commit=False)
            was_hidden = temp_project.hide

            if 'save_draft' in self.request.POST:
                temp_project.hide = True
            elif 'publish' in self.request.POST:
                temp_project.hide = False
                if was_hidden:
                    # 프로젝트가 완전히 게시된 경우에만 포인트 증가
                    profile = self.request.user
                    profile.points += 10  # 프로젝트 게시 시 10 포인트 증가
                    while profile.points >= 100:
                        profile.level += 1  # 100 포인트마다 레벨 1 증가
                        profile.points -= 100  # 레벨 업 후 포인트 조정
                    profile.save()
            elif not temp_project.hide:  # 일반적인 업데이트
                profile = self.request.user
                profile.points += 3  # 프로젝트 수정 시 3 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()
            
            temp_project.save()

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in temp_project.detailed_descriptions.all()}
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
                    Description.objects.create(project=temp_project, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # 프로젝트 수정 로그 기록
            update_description = "프로젝트 수정로그: "
            for field in form.cleaned_data:
                if field != 'image':
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')
            
            # 현재의 detailed_descriptions을 문자열로 변환하여 로그 메시지에 추가
            detailed_descriptions_str = "; ".join(
                [f"{desc.name}: {desc.text}" for desc in temp_project.detailed_descriptions.all()]
            )
            update_description += f"\n추가정보 수정로그: {detailed_descriptions_str}"

            ProjectUpdateLog.objects.create(
                project=temp_project,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_project.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projectapp:detail', kwargs={'pk': self.object.pk})

@login_required
@require_POST
def project_delete_description(request):
    description_id = request.POST.get('id')
    try:
        description = Description.objects.get(id=description_id)
        if description.project.writer == request.user:  # 작성자 확인
            description.delete()
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': '권한이 없습니다.'}, status=403)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': '설명이 존재하지 않습니다.'}, status=404)



def events_api(request):
    # 쿼리 파라미터에서 프로젝트 ID를 가져옵니다.
    project_id = request.GET.get('project_id')
    
    if project_id:
        # 특정 프로젝트에 속하는 Article만 필터링
        events = Article.objects.filter(hide=False, project__id=project_id)
    else:
        # 프로젝트 ID가 제공되지 않은 경우, 모든 Article을 반환합니다.
        # 이 부분은 필요에 따라 제거하거나 다르게 처리할 수 있습니다.
        events = Article.objects.all()
    
    events_list = [{
        'title': event.title,
        'start': event.date.strftime("%Y-%m-%d") if event.date else '',
        'url': f'/articles/detail/{event.id}',
        'color': 'blue',
    } for event in events]
    
    return JsonResponse(events_list, safe=False)

def project_update_log_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    update_logs = ProjectUpdateLog.objects.filter(project=project).order_by('-updated_at')
    
    context = {
        'project': project,
        'update_logs': update_logs,
    }
    return render(request, 'projectapp/project_update_logs.html', context)