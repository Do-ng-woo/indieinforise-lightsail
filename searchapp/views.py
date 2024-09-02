from django.shortcuts import render

# Create your views here.
# views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.apps import apps

from articleapp.models import Article  # 기존 Article 모델을 임포트합니다.
from artistapp.models import Artist
from projectapp.models import Project
from personapp.models import Person
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from communityapp.models import Community


def search_view(request):
    query = request.GET.get('q', '')  # 검색어를 쿼리 파라미터로 받습니다.
    results_per_page = 10  # 페이지당 보여줄 결과 수

    context = {
        'query': query,
        'message': '',  # 사용자에게 보여줄 메시지
    }

    if query:
        
        if len(query) < 2:
            context['message'] = '두 글자 이상부터 검색 가능합니다.'
            return render(request, 'searchapp/result.html', context)
        # 공연
        article_query = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(article_query, results_per_page)
        context['article_results'] = paginator.get_page(1)
        context['article_count'] = article_query.count()

        # 아티스트
        artist_query = Artist.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(artist_query, results_per_page)
        context['artist_results'] = paginator.get_page(1)
        context['artist_count'] = artist_query.count()

        # 공연장
        project_query = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(project_query, results_per_page)
        context['project_results'] = paginator.get_page(1)
        context['project_count'] = project_query.count()

        # 인물
        person_query = Person.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(person_query, results_per_page)
        context['person_results'] = paginator.get_page(1)
        context['person_count'] = person_query.count()

        # 노래
        sing_query = Sing.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(sing_query, results_per_page)
        context['sing_results'] = paginator.get_page(1)
        context['sing_count'] = sing_query.count()

        # 장르
        genre_query = Genre.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(genre_query, results_per_page)
        context['genre_results'] = paginator.get_page(1)
        context['genre_count'] = genre_query.count()

        # 앨범
        album_query = Album.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(album_query, results_per_page)
        context['album_results'] = paginator.get_page(1)
        context['album_count'] = album_query.count()

        # 커뮤니티
        community_query = Community.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        paginator = Paginator(community_query, results_per_page)
        context['community_results'] = paginator.get_page(1)
        context['community_count'] = community_query.count()

    return render(request, 'searchapp/result.html', context)


# 모델 구성 설정
MODEL_CONFIG = {
    'article': {
        'app_name': 'articleapp',
        'filter_fields': {'title': 'icontains', 'content': 'icontains'},
        'url_pattern': '/articles/detail/{id}'
    },
    'artist': {
        'app_name': 'artistapp',
        'filter_fields': {'title': 'icontains', 'description': 'icontains'},
        'url_pattern': '/artists/detail/{id}'
    },
    'project': {
        'app_name': 'projectapp',
        'filter_fields': {'title': 'icontains', 'description': 'icontains'},
        'url_pattern': '/projects/detail/{id}'
    },
    'person': {
        'app_name': 'personapp',
        'filter_fields': {'title': 'icontains', 'description': 'icontains'},
        'url_pattern': '/persons/detail/{id}'
    },
    'sing': {
        'app_name': 'singapp',
        'filter_fields': {'title': 'icontains', 'content': 'icontains'},
        'url_pattern': '/sings/detail/{id}'
    },
    'album': {
        'app_name': 'albumapp',
        'filter_fields': {'title': 'icontains', 'content': 'icontains'},
        'url_pattern': '/albums/detail/{id}'
    },
    'genre': {
        'app_name': 'genreapp',
        'filter_fields': {'title': 'icontains', 'content': 'icontains'},
        'url_pattern': '/genres/detail/{id}'
    },
    'community': {
        'app_name': 'communityapp',
        'filter_fields': {'title': 'icontains', 'content': 'icontains'},
        'url_pattern': '/community/detail/{id}'
    },
    # 추가 모델 설정
}

def load_more_data(request, model_name):
    config = MODEL_CONFIG.get(model_name)
    if not config:
        return JsonResponse({'error': 'Invalid model name'}, status=400)

    model = apps.get_model(config['app_name'], model_name)
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    results_per_page = 10

    if query and model:
        filters = Q()
        for field, lookup in config['filter_fields'].items():
            filters |= Q(**{f"{field}__{lookup}": query})
        
        data_query = model.objects.filter(filters).order_by('-created_at')
        paginator = Paginator(data_query, results_per_page)
        data_page = paginator.get_page(page_number)

        data_list = [{
            'id': item.id,
            'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),  # Handles different attribute names
            'created_at': item.created_at.strftime('%Y년 %m월 %d일'),
            'url': config['url_pattern'].format(id=item.id)
        } for item in data_page]

        return JsonResponse({
            'data': data_list,
            'has_next': data_page.has_next(),
            'next_page_number': data_page.next_page_number() if data_page.has_next() else None
        })
    else:
        return JsonResponse({'error': 'No query provided'}, status=400)
    