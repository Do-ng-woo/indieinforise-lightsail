from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from albumapp.decorators import album_ownership_required


from albumapp.forms import AlbumCreationForm, AlbumUpdateForm, AlbumSearchForm
from albumapp.models import Album,Subtitle,Description,AlbumUpdateLog
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
from singapp.models import Sing

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
from django.core import serializers
import json
from django.db.models import F

# Create your views here.
@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class AlbumCreateView(CreateView):
    model = Album
    form_class = AlbumCreationForm
    template_name = 'album/create.html'
    
    def form_valid(self, form):
        if self.request.user.level < 0:
            messages.warning(self.request, "앨범을 작성할 등급이 안됩니다.")
            return redirect('albumapp:list')
        
        with transaction.atomic():
            temp_album = form.save(commit=False)
            temp_album.writer = self.request.user

            if 'save_draft' in self.request.POST:
                temp_album.hide = True
            elif 'publish' in self.request.POST:
                temp_album.hide = False
                profile = self.request.user
                profile.points += 10  # 앨범 생성 시 10 포인트 증가
                while profile.points >= 100:
                    profile.level += 1  # 100 포인트마다 레벨 1 증가
                    profile.points -= 100  # 레벨 업 후 포인트 조정
                profile.save()

            temp_album.save()
            # form.save_m2m()을 호출해 Many-to-Many 데이터 저장
            form.save_m2m()

            self._save_sings(temp_album)
            self._save_text_sings(temp_album)

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
                Description.objects.create(album=temp_album, name=desc['name'], text=desc['text'])

            # 앨범 생성 로그 기록
            update_description = "Album created with the following details: "
            for field in form.cleaned_data:
                if field != 'image':  # 이미지 필드 제외
                    update_description += f"{field}: {form.cleaned_data[field]}, "
            update_description = update_description.rstrip(', ')

            AlbumUpdateLog.objects.create(
                album=temp_album,
                updated_by=self.request.user,
                update_description=update_description,
                hide=temp_album.hide  # hide 상태 기록
            )

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.level < 0:
            messages.warning(request, "앨범을 작성할 등급이 안됩니다")
            return redirect('albumapp:list')
        return super().dispatch(request, *args, **kwargs)
    
    def _save_sings(self, album):
        singCounter = 0
        while True:
            selection_method_key = f'selection_method_{singCounter}'
            if selection_method_key not in self.request.POST:
                break

            selection_method = self.request.POST[selection_method_key]
            if selection_method == 'load':
                sing_id = self.request.POST.get(f'sing_id_{singCounter}', '')
                if sing_id:
                    sing = Sing.objects.get(id=sing_id)
                    album.sing.add(sing)
            singCounter += 1
            
    def _save_text_sings(self, album):
        text_sing_data = []
        singCounter = 0
        while True:
            selection_method_key = f'selection_method_{singCounter}'
            if selection_method_key not in self.request.POST:
                break

            selection_method = self.request.POST[selection_method_key]
            if selection_method == 'manual_entry':
                title = self.request.POST.get(f'manual_artist_{singCounter}', '')
                details = self.request.POST.get(f'manual_title_{singCounter}', '')
                if title and details:
                    sing_info = f'{title}|{details}'  # title과 details를 "|" 문자로 구분하여 저장
                    text_sing_data.append(sing_info)
            singCounter += 1

        if text_sing_data:
            album.text_sing = text_sing_data  # 문자열 리스트를 저장
            album.save()
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 모든 아티스트를 컨텍스트에 추가
        context['artists'] = Artist.objects.filter(hide=False)
        return context
    
    def get_success_url(self):
        return reverse('albumapp:detail', kwargs={'pk':self.object.pk})

class AlbumDetailView(DetailView, FormMixin):
    model = Album
    form_class = CommentCreationForm
    context_object_name = 'target_album'
    template_name = 'albumapp/detail.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        album = self.object
        album.views += 1  # 조회수 1 증가
        album.save(update_fields=['views'])  # 변경된 조회수를 데이터베이스에 저장
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
        user = self.request.user
        today = timezone.now().date()
        

        # Community 페이지네이션
        community_articles = Community.objects.filter(album=album).order_by('-created_at')
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
        
        #케러셀 로직 ------------------
        # Album 인스턴스에 연결된 모든 Artist 인스턴스를 조회
        # Album 인스턴스에 연결된 모든 Artist 인스턴스를 조회
        related_artists = album.artist.all()
        context['related_artists'] = related_artists
        
        if related_artists.exists():
            # Q 객체를 사용하여 여러 Artist 조건을 OR로 결합하여 Article 조회
            articles_query = Q()
            for artist in related_artists:
                articles_query |= Q(artist=artist)
            
            articles = Article.objects.filter(articles_query,hide=False).annotate(
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
        
        text_sings = []
        if album.text_sing:
            for item in album.text_sing:
                parts = item.split("|") if "|" in item else [item, ""]
                text_sings.append(parts)

        context['text_sings'] = text_sings

        return context

        return context
    
class AlbumListView(ListView):
    model = Album
    context_object_name = 'album_list'
    template_name = 'albumapp/list.html'
    paginate_by = 12
    
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
        context['search_form'] = AlbumSearchForm(self.request.GET or None)
        context['search_field'] = self.request.GET.get('search_field', 'title')  # 검색 필드 추가
        return context
    
@method_decorator(album_ownership_required, 'get')
@method_decorator(album_ownership_required, 'post')
class AlbumDeleteView(DeleteView):
    model = Album
    context_object_name='target_album'
    success_url = reverse_lazy('albumapp:list')
    template_name = 'albumapp/delete.html' 
    
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
class AlbumUpdateView(UpdateView):
    model = Album
    form_class = AlbumUpdateForm
    context_object_name = 'target_album'
    template_name = 'albumapp/update.html'
    
    def get(self, request, *args, **kwargs): #subtitle 기존에 입력된것 나타나게 하기
        self.object = self.get_object()
        form = self.get_form()

        # 여기서 기존 데이터를 폼에 채워 넣음
        form.fields['sub_titles_input'].initial = ', '.join(self.object.sub_titles.values_list('name', flat=True))

        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        referer_url = request.META.get('HTTP_REFERER')
        if request.user.level < 0:
            messages.error(request, "You do not have permission to edit this album.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트

        now = timezone.now()
        # 현재 시간 기준으로 10분 이내에 같은 사용자가 hide되지 않은 전체 앨범 수정한 로그의 수를 카운트
        recent_logs_count = AlbumUpdateLog.objects.filter(
            updated_by=request.user,
            updated_at__gte=now - timedelta(minutes=10),
            hide=False
        ).count()
        
        # 10분 이내에 3회 이상 수정 시도를 확인하고 차단
        if recent_logs_count >= 100:
            messages.error(request, "You have reached the edit limit for the last 10 minutes.")
            return redirect(referer_url if referer_url else '/')  # Referer가 없는 경우 홈으로 리다이렉트
        
        return super().dispatch(request, *args, **kwargs)
       
    def form_valid(self, form):
        with transaction.atomic():  # 데이터 처리를 트랜잭션으로 묶음
            album = form.save(commit=False)
            was_hidden = album.hide

            if 'save_draft' in self.request.POST:
                album.hide = True
            elif 'publish' in self.request.POST:
                album.hide = False
                if was_hidden:
                    profile = self.request.user
                    profile.points += 10
                    while profile.points >= 100:
                        profile.level += 1
                        profile.points -= 100
                    profile.save()
            elif not album.hide:
                profile = self.request.user
                profile.points += 3
                while profile.points >= 100:
                    profile.level += 1
                    profile.points -= 100
                profile.save()

            album.save()

            # 기존 설명 업데이트
            existing_descriptions = {desc.id: desc for desc in album.detailed_descriptions.all()}
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
                    Description.objects.create(album=album, name=desc['name'], text=desc['text'])

            # 삭제되지 않은 기존 설명 삭제
            for remaining_desc in existing_descriptions.values():
                remaining_desc.delete()

            # Sing 및 TextSing 데이터 처리
            self.update_sings(album)

            # 앨범 수정 로그 기록
            update_description = "앨범 업데이트 로그: "
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
                [f"{desc.name}: {desc.text}" for desc in album.detailed_descriptions.all()]
            )
            update_description += f"\n 세부정보입력: {detailed_descriptions_str}"

            # 현재의 sing 및 text_sing 정보를 문자열로 변환하여 로그 메시지에 추가
            text_sings_str = ", ".join(album.text_sing)

            # 앨범 수정 로그에 추가 정보 포함
            update_description += f" 직접입력한 멤버: {text_sings_str}."

            AlbumUpdateLog.objects.create(
                album=album,
                updated_by=self.request.user,
                update_description=update_description,
                hide=album.hide  # hide 상태 기록
            )

        return super().form_valid(form)


    
    def update_sings(self, album):
        # JSON 문자열을 안전하게 파싱하는 함수
        def safe_json_loads(s):
            try:
                return json.loads(s) if s else []
            except json.JSONDecodeError:
                return []

        # 최종 선택된 노래 ID 정보 파싱
        final_sing_ids = self.request.POST.get('final_sings', '[]')
        if final_sing_ids:
            final_sing_ids = safe_json_loads(final_sing_ids)

        # 최종 직접 입력한 노래 정보 파싱 및 변환
        final_text_sings_str = safe_json_loads(self.request.POST.get('final_text_sings', ''))
        final_text_sings_converted = []

        for item in final_text_sings_str:
            if isinstance(item, str) and ':' in item:
                parts = item.split(':', 1)  # 최대 1번만 분리하여 아티스트와 제목 분리
                if len(parts) == 2:
                    artist, title = parts
                    final_text_sings_converted.append((artist.strip(), title.strip()))
                else:
                    # 형식이 맞지 않는 경우 예외 처리
                    pass

        # 선택된 노래 ID 정보를 앨범 모델의 관련 필드에 저장 (예제 코드는 가정)
        album.sing.set(final_sing_ids)

        # 직접 입력한 노래 정보를 앨범 모델의 text_sing 필드에 저장
        text_sing_data = [f'{artist}|{title}' for artist, title in final_text_sings_converted]

        # 텍스트 노래 데이터가 없으면 빈 리스트로 설정하여 필드 비우기
        album.text_sing = text_sing_data if text_sing_data else []
        album.save()

            
    def get_context_data(self, **kwargs):
        context = super(AlbumUpdateView, self).get_context_data(**kwargs)
        context['artists'] = Artist.objects.filter(hide=False)

        # 기존 context 설정 코드 유지
        if self.request.POST:
            context['detailed_descriptions'] = self.request.POST.getlist('detailed_descriptions')
        else:
            context['detailed_descriptions'] = [desc.text for desc in self.object.detailed_descriptions.all()]
        
        # 이미 입력한 불러오기를 통한 멤버와 포지션 정보 불러오기
        sings_with_artists = []
        for sing in self.object.sing.filter(hide=False):
            artist_info = sing.artist.first()
            if artist_info:
                sings_with_artists.append({
                    'sing_id': sing.id,
                    'artist_id': artist_info.id,
                    'artist_title': artist_info.title,
                    'sing_title': sing.title,
                })
        print(sings_with_artists)  # 이 줄을 추가하여 결과를 확인
        context['sings_with_artists'] = sings_with_artists
        #이미 입력한 직접 입력하기를 통한 멤버와 포지션 정보 불러오기
        
        text_sings_data = []
        for text_sing in self.object.text_sing:
            parts = text_sing.split('|')  # "|"를 구분자로 사용하여 저장했다고 가정
            if len(parts) == 2:
                artist, title = parts
            else:
                artist = parts[0] if parts else ''
                title = ''
            text_sings_data.append({'artist': artist, 'title': title})
        context['text_sings_data'] = text_sings_data

        context['albums'] = Album.objects.filter(hide=False)  # 사용하는 모델과 필드명에 따라 조정 필요

        return context

    def get_success_url(self):
        return reverse('albumapp:detail', kwargs={'pk': self.object.pk})
    

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
    

def album_update_log_view(request, pk):
    album = get_object_or_404(Album, pk=pk)
    update_logs = AlbumUpdateLog.objects.filter(album=album).order_by('-updated_at')
    
    context = {
        'album': album,
        'update_logs': update_logs,
    }
    return render(request, 'albumapp/album_update_logs.html', context)



def get_songs_by_artist(request, artist_id):
    songs = Sing.objects.filter(hide=False,artist__id=artist_id).values('id', 'title')
    songs_list = list(songs)  # QuerySet을 리스트로 변환
    return JsonResponse({'songs': songs_list}, safe=False)
    
