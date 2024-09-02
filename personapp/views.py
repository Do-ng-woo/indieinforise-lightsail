from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from personapp.decorators import person_ownership_required


from personapp.forms import PersonCreationForm, PersonUpdateForm
from personapp.models import Person,Subtitle,Description,PersonUpdateLog
from articleapp.models import Article
from artistapp.models import Artist
from instrumentapp.models import Instrument
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

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class PersonCreateView(CreateView):
    model = Person
    form_class = PersonCreationForm
    template_name = 'person/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 0:
            messages.warning(self.request, "인물정보를 작성할 등급이 안됩니다.")
            return redirect('personapp:list')
        
        with transaction.atomic():
            temp_person = form.save(commit=False)
            temp_person.writer = self.request.user

            if 'save_draft' in self.request.POST:
                temp_person.hide = True
            elif 'publish' in self.request.POST:
                temp_person.hide = False
                profile = self.request.user
                profile.points += 10  # 인물 생성 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_person.save()

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
                Description.objects.create(person=temp_person, name=desc['name'], text=desc['text'])

            # 인물 생성 로그 기록
            update_description = "Person created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            PersonUpdateLog.objects.create(
                person=temp_person,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_person.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 0:
            messages.warning(request, "인물정보를 작성할 등급이 안됩니다")
            return redirect('personapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('personapp:detail', kwargs={'pk': self.object.pk})

class PersonDetailView(DetailView, FormMixin):
    model = Person
    form_class = CommentCreationForm
    context_object_name = 'target_person'
    template_name = 'personapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        person = self.object
        person.views += 1  # 조회수 1 증가
        person.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object
        user = self.request.user
        today = timezone.now().date()

        # 인증된 사용자에 대한 구독 정보 처리
        if user.is_authenticated:
            context['subscription'] = Per_Subscription.objects.filter(user=user, person=person)
        else:
            context['subscription'] = None

        # Person 인스턴스에 연결된 모든 Artist 인스턴스를 조회
        related_artists = Artist.objects.filter(person=person)
        context['related_artists'] = related_artists

        if related_artists.exists():
            # Q 객체를 사용하여 여러 Artist 조건을 OR로 결합
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
            
            if future_articles_sorted:
                initial_slide_index = len(past_articles_sorted)
            else:
                initial_slide_index = len(past_articles_sorted) - 1 if past_articles_sorted else 0

        else:
            all_articles_sorted = []
            initial_slide_index = 0

        # context에 추가
        context['all_articles'] = all_articles_sorted
        context['initial_slide_index'] = initial_slide_index

        # Community 페이지네이션
        community_articles = Community.objects.filter(person=person).order_by('-created_at')
        community_page = self.request.GET.get('community_page', 1)
        community_paginator = Paginator(community_articles, 5)  # 페이지당 5개의 객체
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

class PersonListView(ListView):
    model = Person
    context_object_name = 'person_list'
    template_name = 'personapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(hide=False)
        search_keyword = self.request.GET.get('search_keyword', '')
        instrument_ids = self.request.GET.getlist('instruments', '')

        if search_keyword:
            queryset = queryset.filter(title__icontains=search_keyword)
        
        if instrument_ids:
            queryset = queryset.filter(instruments__in=instrument_ids).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instrument_choices'] = Instrument.objects.all()
        context['search_keyword'] = self.request.GET.get('search_keyword', '')
        context['selected_instruments'] = self.request.GET.getlist('instruments', '')
        return context
    
@method_decorator(person_ownership_required, 'get')
@method_decorator(person_ownership_required, 'post')
class PersonDeleteView(DeleteView):
    model = Person
    context_object_name='target_person'
    success_url = reverse_lazy('personapp:list')
    template_name = 'personapp/delete.html' 
    
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
class PersonUpdateView(UpdateView):
    model = Person
    form_class = PersonUpdateForm
    context_object_name = 'target_person'
    template_name = 'personapp/update.html'
    
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
            messages.error(request, "You do not have permission to edit this person.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 인물 수정한 로그의 수를 카운트
        recent_logs_count = PersonUpdateLog.objects.filter(
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
        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]
        return context

    def form_valid(self, form):
        with transaction.atomic():
            person = form.save(commit=False)
            was_hidden = person.hide

            if 'save_draft' in self.request.POST:
                person.hide = True
            elif 'publish' in self.request.POST:
                person.hide = False
                if was_hidden:
                    # 인물이 완전히 게시된 경우에만 포인트 증가
                    profile = self.request.user
                    profile.points += 10  # 인물 게시 시 10 포인트 증가
                    while profile.points >= 100:
                        profile.level += 1  # 100 포인트마다 레벨 1 증가
                        profile.points -= 100  # 레벨 업 후 포인트 조정
                    profile.save()
            elif not person.hide:  # 일반적인 업데이트
                profile = self.request.user
                profile.points += 3  # 인물 수정 시 3 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            person.save()

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in person.detailed_descriptions.all()}
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
                    Description.objects.create(person=person, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # 인물 수정 로그 기록
            update_description = "인물정보 업데이트 로그: "
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
                [f"{desc.name}: {desc.text}" for desc in person.detailed_descriptions.all()]
            )
            update_description += f"\n 추가 입력한 정보: {detailed_descriptions_str}"

            # Person 수정 로그 기록
            PersonUpdateLog.objects.create(
                person=person,
                updated_by=self.request.user,
                update_description=update_description,
                hide=person.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('personapp:detail', kwargs={'pk': self.object.pk})
    
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
    

def person_update_log_view(request, pk):
    person = get_object_or_404(Person, pk=pk)
    update_logs = PersonUpdateLog.objects.filter(person=person).order_by('-updated_at')
    
    context = {
        'person': person,
        'update_logs': update_logs,
    }
    return render(request, 'personapp/person_update_logs.html', context)