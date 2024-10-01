from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from instrumentapp.decorators import instrument_ownership_required


from instrumentapp.forms import InstrumentCreationForm, InstrumentUpdateForm, InstrumentSearchForm
from instrumentapp.models import Instrument,Subtitle,Description,InstrumentUpdateLog
from articleapp.models import Article
from artistapp.models import Artist
from personapp.models import Person
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
from django.db.models import F, FloatField

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class InstrumentCreateView(CreateView):
    model = Instrument
    form_class = InstrumentCreationForm
    template_name = 'instrument/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 0:
            messages.warning(self.request, "장르를 작성할 등급이 안됩니다.")
            return redirect('instrumentapp:list')
        
        with transaction.atomic():
            temp_instrument = form.save(commit=False)
            temp_instrument.writer = self.request.user

            if 'save_draft' in self.request.POST:
                temp_instrument.hide = True
            elif 'publish' in self.request.POST:
                temp_instrument.hide = False
                profile = self.request.user
                profile.points += 10  # Instrument 게시 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_instrument.save()
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
                Description.objects.create(instrument=temp_instrument, name=desc['name'], text=desc['text'])

            # Instrument 생성 로그 기록
            update_description = "Instrument created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            InstrumentUpdateLog.objects.create(
                instrument=temp_instrument,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_instrument.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 0:
            messages.warning(request, "아티스트를 작성할 등급이 안됩니다")
            return redirect('instrumentapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('instrumentapp:detail', kwargs={'pk':self.object.pk})
    


class InstrumentDetailView(DetailView, FormMixin):
    model = Instrument
    form_class = CommentCreationForm
    context_object_name = 'target_instrument'
    template_name = 'instrumentapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        instrument = self.object
        instrument.views += 1  # 조회수 1 증가
        instrument.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = self.object
        user = self.request.user
        today = timezone.now().date()
        

        # Community 페이지네이션
        community_articles = Community.objects.filter(instrument=instrument).order_by('-created_at')
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

        # 해당 악기에 대한 인기 멤버를 계산
        popular_persons = Person.objects.filter(instruments=instrument).annotate(
            points=Coalesce(F('like') * 0.7 + F('views') * 0.3, 0, output_field=FloatField())
        ).order_by('-points')[:5]

        context['popular_persons'] = popular_persons

        return context
    
class InstrumentListView(ListView):
    model = Instrument
    context_object_name = 'instrument_list'
    template_name = 'instrumentapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(hide=False)
        search_keyword = self.request.GET.get('search_keyword', '')
        search_field = self.request.GET.get('search_field', '')

        if search_field == 'title' and search_keyword:
            # 제목으로 검색
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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = InstrumentSearchForm(self.request.GET or None)
        context['search_field'] = self.request.GET.get('search_field', 'title')  # 검색 필드 추가
        return context
    
@method_decorator(instrument_ownership_required, 'get')
@method_decorator(instrument_ownership_required, 'post')
class InstrumentDeleteView(DeleteView):
    model = Instrument
    context_object_name='target_instrument'
    success_url = reverse_lazy('instrumentapp:list')
    template_name = 'instrumentapp/delete.html' 
    
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
class InstrumentUpdateView(UpdateView):
    model = Instrument
    form_class = InstrumentUpdateForm
    context_object_name = 'target_instrument'
    template_name = 'instrumentapp/update.html'
    
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
            messages.error(request, "You do not have permission to edit this instrument.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 장르 수정한 로그의 수를 카운트
        recent_logs_count = InstrumentUpdateLog.objects.filter(
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
        context = super(InstrumentUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]
        return context

    def form_valid(self, form):
        with transaction.atomic():
            instrument = form.save(commit=False)
            was_hidden = instrument.hide

            if 'save_draft' in self.request.POST:
                instrument.hide = True
            elif 'publish' in self.request.POST:
                instrument.hide = False
                if was_hidden:
                    # 장르가 완전히 게시된 경우에만 포인트 증가
                    profile = self.request.user
                    profile.points += 10  # 장르 게시 시 10 포인트 증가
                    while profile.points >= 100:
                        profile.level += 1  # 100 포인트마다 레벨 1 증가
                        profile.points -= 100  # 레벨 업 후 포인트 조정
                    profile.save()
            elif not instrument.hide:  # 일반적인 업데이트
                profile = self.request.user
                profile.points += 3  # 장르 수정 시 3 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            instrument.save()
            form.save_m2m()  # ManyToMany 필드를 저장합니다.

            # ManyToMany 필드 동적 처리
            origins_ids = self.request.POST.getlist('origins')
            if origins_ids:
                instrument.origins.set(Instrument.objects.filter(id__in=origins_ids))

            subinstruments_ids = self.request.POST.getlist('subinstruments')
            if subinstruments_ids:
                instrument.subinstruments.set(Instrument.objects.filter(id__in=subinstruments_ids))

            derived_instruments_ids = self.request.POST.getlist('derived_instruments')
            if derived_instruments_ids:
                instrument.derived_instruments.set(Instrument.objects.filter(id__in=derived_instruments_ids))

            related_instruments_ids = self.request.POST.getlist('related_instruments')
            if related_instruments_ids:
                instrument.related_instruments.set(Instrument.objects.filter(id__in=related_instruments_ids))

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in instrument.detailed_descriptions.all()}
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
                    existing_description = existing_descriptions[int(description_id)]
                    existing_description.name = desc['name']
                    existing_description.text = desc['text']
                    existing_description.save()
                    del existing_descriptions[int(description_id)]
                else:
                    Description.objects.create(instrument=instrument, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # 장르 수정 로그 기록
            update_description = "장르 정보 업데이트 로그: "
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
                [f"{desc.name}: {desc.text}" for desc in instrument.detailed_descriptions.all()]
            )
            update_description += f"\n 추가 입력한 정보: {detailed_descriptions_str}"

            # Instrument 수정 로그 기록
            InstrumentUpdateLog.objects.create(
                instrument=instrument,
                updated_by=self.request.user,
                update_description=update_description,
                hide=instrument.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('instrumentapp:detail', kwargs={'pk': self.object.pk})
    
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
    

def instrument_update_log_view(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    update_logs = InstrumentUpdateLog.objects.filter(instrument=instrument).order_by('-updated_at')
    
    context = {
        'instrument': instrument,
        'update_logs': update_logs,
    }
    return render(request, 'instrumentapp/instrument_update_logs.html', context)

