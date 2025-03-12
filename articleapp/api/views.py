from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import get_object_or_404

from articleapp.models import Article
from communityapp.models import Community
from commentapp.models import Comment
from articleapp.api.serializers import ArticleSerializer
from commentapp.api.serializers import CommentSerializer
from communityapp.api.serializers import CommunitySerializer


from rest_framework.pagination import PageNumberPagination

from rest_framework.generics import ListAPIView
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.utils import timezone



class ArticleDetailAPIView(APIView):
    """
    ✅ 특정 기사(Article) 상세 정보를 가져오는 API
    - 조회수 증가 포함
    - 관련 커뮤니티 및 댓글 포함
    """

    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)

        # ✅ 조회수 증가
        article.views += 1
        article.save(update_fields=['views'])

        # ✅ Article 데이터 직렬화
        serialized_article = ArticleSerializer(article).data

        # ✅ 관련 커뮤니티 데이터 (최신순, 10개 제한)
        tagged_communities = Community.objects.filter(article=article).order_by('-created_at')
        community_paginator = Paginator(tagged_communities, 10)
        community_page = request.GET.get('community_page', 1)
        community_articles = community_paginator.get_page(community_page)
        serialized_communities = CommunitySerializer(community_articles, many=True).data

        # ✅ 댓글 데이터 가져오기
        content_type = ContentType.objects.get_for_model(article)
        comments = Comment.objects.filter(content_type=content_type, object_id=article.pk) \
                                  .annotate(likes_count=Count('likes'))

        # ✅ URL 쿼리에 따라 정렬 방식 결정
        sort = request.GET.get('sort', 'new')  # 기본 정렬: 최신순
        if sort == 'likes':
            comments = comments.order_by('-likes_count', '-created_at')
        else:
            comments = comments.order_by('-created_at')

        # ✅ 댓글 페이징 처리
        comment_paginator = Paginator(comments, 10)
        comment_page_number = request.GET.get('comment_page', 1)
        comment_page = comment_paginator.get_page(comment_page_number)
        serialized_comments = CommentSerializer(comment_page, many=True).data

        return Response({
            "article": serialized_article,
            "community_articles": serialized_communities,
            "comments": serialized_comments,
            "total_comments": comments.count(),
            "total_communities": tagged_communities.count(),
            "sort": sort,
        }, status=status.HTTP_200_OK)
    

from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import Q

from articleapp.models import Article
from articleapp.api.serializers import ArticleSerializer

class ArticlePagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = 'page_size'
    max_page_size = 100  # 최대 페이지 크기

class ArticleListAPIView(ListAPIView):
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        now = timezone.now()  # 현재 날짜 및 시간

        # 기본 필터: 숨겨진(hide=True) 공연 제외
        queryset = Article.objects.filter(hide=False).annotate(
            sort_date=Coalesce('datetime', 'date')  # datetime 없으면 date 사용
        )

        filter_type = self.request.GET.get('type', 'new')  # 기본값 'new'

        if filter_type == 'upcoming':
            # 🎭 다가오는 공연 - 현재 시간보다 미래 공연만 가져오기
            queryset = queryset.filter(sort_date__gte=now).order_by('sort_date')
        
        elif filter_type == 'popular':
            # 🎟 인기순 - 현재 이후의 공연만 조회수 높은 순
            queryset = queryset.filter(sort_date__gte=now).order_by('-views', 'sort_date')
        
        else:
            # 🆕 최신 작성순
            queryset = queryset.order_by('-created_at')

        return queryset
    
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict
from datetime import timedelta
from django.utils import timezone
from articleapp.models import Article
from artistapp.models import Artist
from articleapp.api.serializers import ArticleSerializer

class SearchPagination(PageNumberPagination):
    """🔄 페이지네이션 설정"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class SearchPerformanceAPIView(APIView):
    """🔍 공연 검색 API (미래, 최근 1년, 1년 이상 전)"""
    pagination_class = SearchPagination  # ✅ 페이지네이션 클래스 추가

    def get(self, request):
        query = request.GET.get('q', '').replace(' ', '')  # 검색어에서 공백 제거
        if len(query) < 2:
            return Response({"error": "두 글자 이상 입력해주세요."}, status=400)

        current_time = timezone.now()
        one_year_ago = current_time - timedelta(days=365)  # 1년 전
        two_years_ago = current_time - timedelta(days=730)  # 2년 전 (더 과거)

        # 🎵 아티스트 검색 (제목과 부제목)
        matching_artists = Artist.objects.filter(
            Q(title__icontains=query) | 
            Q(sub_titles__name__icontains=query),
            hide=False
        ).distinct()
        artist_ids = matching_artists.values_list('id', flat=True)

        # 🎭 공연 검색
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(artist__title__icontains=query) | 
            Q(project__title__icontains=query) |
            Q(artist__id__in=artist_ids),
            hide=False
        ).distinct()

        # ✅ 미래 공연 (현재 ~ 미래)
        future_performances = articles.filter(
            Q(datetime__gte=current_time) | 
            Q(date__gte=current_time.date())
        ).order_by('datetime')

        # ✅ 최근 1년 공연 (현재 ~ 1년 전)
        past_one_year_performances = articles.filter(
            Q(datetime__range=(one_year_ago, current_time)) | 
            Q(date__range=(one_year_ago.date(), current_time.date()))
        ).order_by('-datetime')

        # ✅ 1년 이상 지난 공연 (1년 전 ~ 2년 전)
        older_performances = articles.filter(
            Q(datetime__lt=one_year_ago) | 
            Q(date__lt=one_year_ago.date())
        ).order_by('-datetime')

        # 🔄 중복 제거
        all_results = list(future_performances) + list(past_one_year_performances) + list(older_performances)
        unique_results = list(OrderedDict((article.id, article) for article in all_results).values())

        # 📌 페이지네이션 적용
        paginator = self.pagination_class()
        page_results = paginator.paginate_queryset(unique_results, request, view=self)

        if page_results is not None:
            serializer = ArticleSerializer(page_results, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response({"results": []})  # ✅ 빈 응답 방지