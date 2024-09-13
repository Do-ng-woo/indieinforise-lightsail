from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from artistapp.decorators import artist_ownership_required
from django.views.generic.edit import FormMixin
from commentapp.forms import CommentCreationForm

from artistapp.forms import ArtistCreationForm, ArtistUpdateForm, ArtistHotPointForm
from artistapp.models import Artist,Subtitle,Description,ArtistUpdateLog, ArtistPointLog, HonoraryEntry
from articleapp.models import Article
from communityapp.models import Community
from personapp.models import Person
from singapp.models import Sing
from instrumentapp.models import Instrument

from subscribeapp.models import A_Subscription

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers import serialize
from django.db import transaction
import uuid
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.serializers import serialize
import json

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

from django.db.models import Case, When, Value, CharField
from django.db.models.functions import Coalesce

from commentapp.models import Comment 
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models import F
from datetime import datetime

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ArtistCreateView(CreateView):
    model = Artist
    form_class = ArtistCreationForm
    template_name = 'artistapp/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 0:
            messages.warning(self.request, "아티스트를 작성할 등급이 안됩니다.")
            return redirect('artistapp:list')
        
        with transaction.atomic():
            temp_artist = form.save(commit=False)
            temp_artist.writer = self.request.user
            
            if 'save_draft' in self.request.POST:
                temp_artist.hide = True
            elif 'publish' in self.request.POST:
                temp_artist.hide = False
                profile = self.request.user
                profile.points += 10  # 아티스트 생성 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_artist.save()

            self._save_descriptions(temp_artist)
            self._save_persons(temp_artist)
            self._save_text_persons(temp_artist)  # 직접 입력한 멤버 정보 저장

            # 아티스트 생성 로그 기록
            update_description = "Artist created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            ArtistUpdateLog.objects.create(
                artist=temp_artist,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_artist.hide  # hide 상태 기록
            )

        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 0:
            messages.warning(request, "아티스트를 작성할 등급이 안됩니다")
            return redirect('artistapp:list')
        return super().dispatch(request, *args, **kwargs)

    def _save_descriptions(self, artist):
        descriptions_data = {}
        for key, value in self.request.POST.items():
            if 'detailed_descriptions' in key:
                index = key.split('[')[1].split(']')[0]
                field_type = key.split('[')[2].split(']')[0]

                if index not in descriptions_data:
                    descriptions_data[index] = {'name': '', 'text': ''}

                if field_type == 'name':
                    descriptions_data[index]['name'] = value
                elif field_type == 'value':
                    descriptions_data[index]['text'] = value

        for desc in descriptions_data.values():
            Description.objects.create(artist=artist, name=desc['name'], text=desc['text'])

    def _save_persons(self, artist):
        memberCounter = 0
        while True:
            selection_method_key = f'selection_method_{memberCounter}'
            if selection_method_key not in self.request.POST:
                break

            selection_method = self.request.POST[selection_method_key]
            if selection_method == 'load':
                person_id = self.request.POST.get(f'person_id_{memberCounter}', '')
                if person_id:
                    person = Person.objects.get(id=person_id)
                    artist.person.add(person)
            # 여기서 "직접 입력하기"에 대한 추가적인 처리를 할 수 있습니다.
            # 예: 직접 입력된 데이터를 다른 필드나 모델에 저장
            memberCounter += 1
    
    def _save_text_persons(self, artist):
        text_person_data = []
        memberCounter = 0
        while True:
            selection_method_key = f'selection_method_{memberCounter}'
            if selection_method_key not in self.request.POST:
                break

            selection_method = self.request.POST[selection_method_key]
            if selection_method == 'manual_entry':
                name = self.request.POST.get(f'manual_name_{memberCounter}', '')
                instrument = self.request.POST.get(f'manual_instrument_{memberCounter}', '')
                if name and instrument:
                    member_info = f'{instrument}: {name}'  # 문자열로 포맷
                    text_person_data.append(member_info)
            memberCounter += 1

        if text_person_data:
            artist.text_person = text_person_data  # 리스트를 저장
            artist.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruments'] = Instrument.objects.all()
        context['persons'] = Person.objects.all()
        return context

    def get_success_url(self):
        return reverse('artistapp:detail', kwargs={'pk': self.object.pk})

class ArtistDetailView(DetailView, FormMixin):
    model = Artist
    form_class = CommentCreationForm
    context_object_name = 'target_artist'
    template_name = 'artistapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        artist = self.object
        artist.views += 1  # 조회수 1 증가
        artist.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.object
        user = self.request.user
        today = timezone.now().date()

        # 인증된 사용자에 대한 구독 정보 처리
        if user.is_authenticated:
            context['subscription'] = A_Subscription.objects.filter(user=user, artist=artist)
        else:
            context['subscription'] = None
        
        #article 넘기기
        # Article 쿼리셋에 sort_date 주석 추가
        articles = Article.objects.filter(artist=artist).annotate(
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
        community_articles = Community.objects.filter(artist=artist).order_by('-created_at')
        community_page = self.request.GET.get('community_page', 1)
        community_paginator = Paginator(community_articles, 5)  # 페이지당 10개의 객체
        context['community_articles'] = community_paginator.get_page(community_page)

        # Sing 객체 리스트화 및 정렬
        sings = Sing.objects.filter(artist=artist).order_by('-like')
        sing_page = self.request.GET.get('sing_page', 1)
        sing_paginator = Paginator(sings, 5)  # 페이지당 5개의 객체
        context['sings'] = sing_paginator.get_page(sing_page)

        text_persons = []
        if artist.text_person:
            # artist.text_person이 리스트인 경우, 이미 분리된 항목을 바로 사용
            for item in artist.text_person:
                # ':'를 기준으로 문자열을 분리
                parts = item.split(":") if ":" in item else [item, ""]
                text_persons.append(parts)
        context['text_persons'] = text_persons
        
        
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

         # 포인트 사용 내역 추가
        point_logs = ArtistPointLog.objects.filter(artist=artist).order_by('-points_used')
        top_users = point_logs[:9]

        context['top_users'] = top_users

        # 사용자 로그인 여부에 따른 처리
        if user.is_authenticated:
            current_user_log = point_logs.filter(user=user).first()
            if current_user_log:
                current_user_rank = list(point_logs).index(current_user_log) + 1
            else:
                current_user_rank = None

            context['current_user_log'] = current_user_log
            context['current_user_rank'] = current_user_rank
        else:
            context['current_user_log'] = None
            context['current_user_rank'] = None
            
        # 전체 아티스트의 핫 랭킹 추가
        hot_rankings = Artist.objects.annotate(
            total_points=F('hot_point') + F('like')
        ).order_by('-hot_point', '-like')[:9]
        context['hot_rankings'] = hot_rankings

        # 현재 아티스트의 핫 랭킹 계산
        all_artists = list(Artist.objects.annotate(
            total_points=F('hot_point') + F('like')
        ).order_by('-hot_point', '-like'))
        current_artist_rank = all_artists.index(artist) + 1
        context['current_artist_rank'] = current_artist_rank
        context['current_artist_hot_points'] = artist.hot_point
        
        # 현재 연도와 분기 계산
        current_year, current_quarter = get_current_year_and_quarter()
        
        # 1년 전 연도와 분기 계산
        last_year, last_quarter = get_previous_year_and_quarter(current_year, current_quarter)

        # 아티스트가 최근 1년 내 명예의 전당에 올랐는지 확인
        recent_entries = HonoraryEntry.objects.filter(
            artist=artist,
            year__gte=last_year,
            year__lte=current_year
        ).exclude(
            year=last_year,
            quarter__lt=last_quarter
        ).exclude(
            year=current_year,
            quarter__gt=current_quarter
        )

        context['can_use_points'] = not recent_entries.exists()

        return context


        

class ArtistListView(ListView):
    model = Artist
    context_object_name = 'artist_list'
    template_name = 'artistapp/list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Artist.objects.filter(hide=False)

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 핫 포인트가 높은 10명의 아티스트 추가
        context['hot_artists'] = Artist.objects.order_by('-hot_point', '-like')[:10]
        
        if self.request.user.is_authenticated:
            user = self.request.user
            user_artist_ids = ArtistPointLog.objects.filter(user=user).values_list('artist_id', flat=True)
            context['user_hot_artists'] = Artist.objects.filter(id__in=user_artist_ids).order_by('-hot_point', '-like')[:10]
        
        # 구독한 아티스트 추가
            subscribed_artist_ids = A_Subscription.objects.filter(user=user).values_list('artist_id', flat=True)
            context['subscribed_artists'] = Artist.objects.filter(id__in=subscribed_artist_ids)[:8]
        return context
        
class HonoraryEntryListView(ListView):
    model = HonoraryEntry
    context_object_name = 'honorary_entry_list'
    template_name = 'artistapp/honorary_list.html'
    paginate_by = 25

    def get_queryset(self):
        queryset = HonoraryEntry.objects.all()

        # 정렬 기준 추가
        order_by = self.request.GET.get('order_by', 'newest')
        if order_by == 'oldest':
            queryset = queryset.order_by('year', 'quarter')
        else:  # 기본값은 'newest'
            queryset = queryset.order_by('-year', '-quarter')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 핫 포인트가 높은 10명의 아티스트 추가
        context['hot_artists'] = Artist.objects.order_by('-hot_point', '-like')[:10]

        if self.request.user.is_authenticated:
            user = self.request.user
            user_artist_ids = ArtistPointLog.objects.filter(user=user).values_list('artist_id', flat=True)
            context['user_hot_artists'] = Artist.objects.filter(id__in=user_artist_ids).order_by('-hot_point', '-like')[:10]

            # 구독한 아티스트 추가
            subscribed_artist_ids = A_Subscription.objects.filter(user=user).values_list('artist_id', flat=True)
            context['subscribed_artists'] = Artist.objects.filter(id__in=subscribed_artist_ids)[:8]

        return context
    
@method_decorator(artist_ownership_required, 'get')
@method_decorator(artist_ownership_required, 'post')
class ArtistDeleteView(DeleteView):
    model = Artist
    context_object_name = 'target_artist'
    success_url = reverse_lazy('artistapp:list')
    template_name = 'artistapp/delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # 서브타이틀 삭제 로직
        with transaction.atomic():
            profile = request.user
            profile.points -= 10  # 프로젝트 삭제 시 10 포인트 감소
            if profile.points < 0:
                profile.level -= 1 
                profile.points += 100
            profile.save()
            
            # 연결된 서브타이틀 삭제
            subtitles = self.object.sub_titles.all()
            for subtitle in subtitles:
                subtitle.delete()

            # 아티스트 삭제
            self.object.delete()
        
        success_url = self.get_success_url()
        return redirect(success_url)
    
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ArtistUpdateView(UpdateView):
    model = Artist
    form_class = ArtistUpdateForm
    context_object_name = 'target_artist'
    template_name = 'artistapp/update.html'
    
    def get(self, request, *args, **kwargs):  # subtitle 기존에 입력된 것을 나타내게 하기
        self.object = self.get_object()
        form = self.get_form()

        # 여기서 기존 데이터를 폼에 채워 넣음
        form.fields['sub_titles_input'].initial = ', '.join(self.object.sub_titles.values_list('name', flat=True))

        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        referer_url = request.META.get('HTTP_REFERER')
        if request.user.level < 0:
            messages.error(request, "You do not have permission to edit this artist.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 아티스트 수정한 로그의 수를 카운트
        recent_logs_count = ArtistUpdateLog.objects.filter(
            updated_by=request.user,
            updated_at__gte=now - timedelta(minutes=10),
            hide=False
        ).count()

        # 10분 이내에 3회 이상 수정 시도를 확인하고 차단
        if recent_logs_count >= 10:
            messages.error(request, "You have reached the edit limit for the last 10 minutes.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():  # 데이터 처리를 트랜잭션으로 묶음
            # Artist 객체 저장
            artist = form.save(commit=False)
            was_hidden = artist.hide

            if 'save_draft' in self.request.POST:
                artist.hide = True
            elif 'publish' in self.request.POST:
                artist.hide = False
                if was_hidden:
                    # 아티스트가 완전히 게시된 경우에만 포인트 증가
                    profile = self.request.user
                    profile.points += 10  # 아티스트 게시 시 10 포인트 증가
                    while profile.points >= 100:
                        profile.level += 1  # 100 포인트마다 레벨 1 증가
                        profile.points -= 100  # 레벨 업 후 포인트 조정
                    profile.save()
            elif not artist.hide:  # 일반적인 업데이트
                profile = self.request.user
                profile.points += 3  # 아티스트 수정 시 3 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            artist.save()

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in artist.detailed_descriptions.all()}
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
                    Description.objects.create(artist=artist, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # Person 및 TextPerson 데이터 처리
            self.update_persons(artist)
            
            # 아티스트 수정 로그 기록
            update_description = "아티스트 업데이트 로그: "
            for field in form.cleaned_data:
                if field != 'image':
                    field_value = form.cleaned_data.get(field, 'N/A')
                    if isinstance(field_value, (list, QuerySet)):
                        field_value = ', '.join(str(item) for item in field_value)
                    update_description += f"{field}: {field_value}, "
            update_description = update_description.rstrip(', ')

            detailed_descriptions_str = "; ".join(
                [f"{desc.name}: {desc.text}" for desc in artist.detailed_descriptions.all()]
            )
            update_description += f"\n 세부정보입력: {detailed_descriptions_str}"

            persons_with_instruments_str = ", ".join([
                f"{person.title} ({', '.join(instr.title for instr in person.instruments.all())})" for person in artist.person.all()
            ])
            text_persons_str = ", ".join(artist.text_person)

            update_description += f" \n 멤버와 악기: {persons_with_instruments_str}."
            update_description += f" 직접입력한 멤버: {text_persons_str}."

            ArtistUpdateLog.objects.create(
                artist=artist,
                updated_by=self.request.user,
                update_description=update_description,
                hide=artist.hide
            )

        return super().form_valid(form)



    def update_persons(self, artist):
        def safe_json_loads(s):
            try:
                return json.loads(s) if s else []
            except json.JSONDecodeError:
                return []

        final_person_ids = self.request.POST.get('final_persons', '[]')
        if final_person_ids:
            final_person_ids = safe_json_loads(final_person_ids)

        final_text_persons_str = safe_json_loads(self.request.POST.get('final_text_persons', ''))
        final_text_persons_converted = []

        for item in final_text_persons_str:
            if isinstance(item, str) and ':' in item:
                final_text_persons_converted.append(item.strip())
            else:
                pass

        artist.person.set(final_person_ids)
        artist.text_person = final_text_persons_converted
        artist.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]

        persons_with_positions = [
            {
                'person_id': person.id,
                'instrument_ids': [instr.id for instr in person.instruments.all()],
                'name': person.title,
            }
            for person in self.object.person.all()
        ]
        context['persons_with_positions'] = persons_with_positions

        text_persons_data = []
        for text_person in self.object.text_person:
            parts = text_person.split(':')
            if len(parts) == 2:
                text_persons_data.append({'instrument': parts[0], 'name': parts[1]})
            else:
                text_persons_data.append({'instrument': '', 'name': text_person})

        context['text_persons_data'] = text_persons_data

        context['persons'] = Person.objects.all()
        context['instruments'] = Instrument.objects.all()

        return context

    def get_success_url(self):
        return reverse('artistapp:detail', kwargs={'pk': self.object.pk})
    
    
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
    

def artist_update_log_view(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    update_logs = ArtistUpdateLog.objects.filter(artist=artist).order_by('-updated_at')
    
    context = {
        'artist': artist,
        'update_logs': update_logs,
    }
    return render(request, 'artistapp/artist_update_logs.html', context)


def get_persons_by_instrument(request, instrument_id):
    try:
        instrument = Instrument.objects.get(id=instrument_id)
        persons = Person.objects.filter(instruments=instrument)  # instrument에 연결된 person을 가져옴
        person_list = [{'id': person.id, 'title': person.title} for person in persons]
        return JsonResponse({'persons': person_list})
    except Instrument.DoesNotExist:
        return JsonResponse({'error': 'Instrument not found'}, status=404)

@login_required
def artist_use_points(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    
    # 현재 연도와 분기 계산
    current_year, current_quarter = get_current_year_and_quarter()
    
    # 1년 전 연도와 분기 계산
    previous_year, previous_quarter = get_previous_year_and_quarter(current_year, current_quarter)

    # 아티스트가 최근 1년 내 명예의 전당에 올랐는지 확인
    recent_entries = HonoraryEntry.objects.filter(
        artist=artist,
        year__gte=previous_year,
        year__lte=current_year
    ).exclude(
        year=previous_year,
        quarter__lt=previous_quarter
    ).exclude(
        year=current_year,
        quarter__gt=current_quarter
    )

    if recent_entries.exists():
        messages.error(request, '이 아티스트는 최근 1년 내에 명예의 전당에 올라 포인트를 사용할 수 없습니다.')
        return redirect('artistapp:detail', pk=artist_id)

    if request.method == 'POST':
        form = ArtistHotPointForm(request.POST)
        if form.is_valid():
            points_to_use = form.cleaned_data['points_to_use']
            user = request.user

            if user.points < points_to_use:
                messages.error(request, '사용할 포인트가 부족합니다.')
            else:
                user.points -= points_to_use
                user.save()
                artist.hot_point += points_to_use
                artist.save()

                # 포인트 사용 로그 추가 또는 업데이트
                point_log, created = ArtistPointLog.objects.get_or_create(user=user, artist=artist)
                if not created:
                    point_log.points_used += points_to_use
                else:
                    point_log.points_used = points_to_use
                point_log.save()

                messages.success(request, '포인트가 성공적으로 사용되었습니다.')
                return redirect('artistapp:detail', pk=artist_id)
    else:
        form = ArtistHotPointForm()

    return redirect('artistapp:detail', pk=artist_id)

def get_current_year_and_quarter():
    now = datetime.now()
    year = now.year
    month = now.month
    quarter = (month - 1) // 3 + 1
    return year, quarter

def get_previous_year_and_quarter(year, quarter):
    if quarter == 1:
        return year - 1, 2  # 현재가 1분기라면, 1년 전 1분기로 설정합니다.
    elif quarter == 2:
        return year - 1, 3  # 현재가 2분기라면, 1년 전 2분기로 설정합니다.
    elif quarter == 3:
        return year - 1, 4  # 현재가 3분기라면, 1년 전 3분기로 설정합니다.
    else:  # quarter == 4
        return year, 1  # 현재가 4분기라면, 1년 전 4분기로 설정합니다.