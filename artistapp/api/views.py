from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Count, F
from django.db.models.functions import Coalesce
from rest_framework import status
from django.contrib.contenttypes.models import ContentType  # 🔹 추가

from artistapp.models import Artist
from articleapp.models import Article
from communityapp.models import Community
from singapp.models import Sing
from commentapp.models import Comment
from artistapp.api.serializers import ArtistSerializer
from articleapp.api.serializers import ArticleSerializer
from communityapp.api.serializers import CommunitySerializer
from singapp.api.serializers import SingSerializer
from commentapp.api.serializers import CommentSerializer


class ArtistDetailAPIView(APIView):
    """🎤 아티스트 상세 API"""

    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)

        # 조회수 증가
        artist.views += 1
        artist.save(update_fields=['views'])

        today = now().date()

        # 🎵 공연(Article) 관련 데이터 정렬 (과거 3개, 미래 5개)
        articles = Article.objects.filter(artist=artist, hide=False).annotate(
            sort_date=Coalesce('datetime', 'date')
        )
        past_articles = list(articles.filter(sort_date__lt=today).order_by('-sort_date')[:3])  # 과거 3개
        future_articles = list(articles.filter(sort_date__gte=today).order_by('sort_date')[:5])  # 미래 5개
        all_articles_sorted = past_articles[::-1] + future_articles

        # Swiper의 initialSlide 값을 설정하기 위한 가장 가까운 미래 게시글의 인덱스 찾기
        initial_slide_index = len(past_articles) if future_articles else max(0, len(past_articles) - 1)

        # 📝 커뮤니티 게시글
        community_articles = Community.objects.filter(artist=artist).order_by('-created_at')

        # 🎼 노래(Sings) 리스트 (좋아요 순)
        sings = Sing.objects.filter(artist=artist).order_by('-like')

        # 🔹 **ContentType을 사용하여 댓글 필터링**
        content_type = ContentType.objects.get_for_model(Artist)  # ✅ Artist 모델의 ContentType 가져오기
        comments = Comment.objects.filter(content_type=content_type, object_id=artist.id) \
                                  .annotate(likes_count=Count('likes')) \
                                  .order_by('-created_at')

        # 📊 핫 랭킹 (좋아요 + 핫포인트 기준)
        hot_rankings = Artist.objects.annotate(
            total_points=F('hot_point') + F('like')
        ).order_by('-hot_point', '-like')[:9]

        # 📌 데이터 직렬화
        serialized_artist = ArtistSerializer(artist).data
        serialized_articles = ArticleSerializer(all_articles_sorted, many=True).data
        serialized_community = CommunitySerializer(community_articles, many=True).data
        serialized_sings = SingSerializer(sings, many=True).data
        serialized_comments = CommentSerializer(comments, many=True).data
        serialized_hot_rankings = ArtistSerializer(hot_rankings, many=True).data

        return Response({
            'artist': serialized_artist,
            'articles': serialized_articles,
            'community_articles': serialized_community,
            'sings': serialized_sings,
            'comments': serialized_comments,
            'total_comments': comments.count(),
            'hot_rankings': serialized_hot_rankings,
            'initial_slide_index': initial_slide_index
        }, status=status.HTTP_200_OK)

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import F
from artistapp.models import Artist
from artistapp.api.serializers import ArtistSerializer

class ArtistPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = 'page_size'
    max_page_size = 100  # 최대 페이지 크기

class ArtistListAPIView(ListAPIView):
    serializer_class = ArtistSerializer
    pagination_class = ArtistPagination

    def get_queryset(self):
        queryset = Artist.objects.filter(hide=False)  # 숨겨진 아티스트 제외

        # 정렬 기준 추가
        order_by = self.request.GET.get('order_by', 'title')  # 기본값: 'title'

        if order_by == 'popularity':
            # 🎟 인기순 - 좋아요(like) 80%, 조회수(views) 20% 가중치 부여
            queryset = queryset.annotate(
                weighted_score=F('like') * 0.8 + F('views') * 0.2
            ).order_by('-weighted_score')
        elif order_by == 'new':
            # 🆕 최신 등록순 - 생성일(created_at) 기준 내림차순
            queryset = queryset.order_by('-created_at')
        else:
            # 🔤 기본값: 제목(title) 기준 오름차순 정렬
            queryset = queryset.order_by('title')

        return queryset


from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q, F
from collections import OrderedDict
from artistapp.models import Artist
from artistapp.api.serializers import ArtistSerializer

class ArtistPagination(PageNumberPagination):
    """✅ 아티스트 리스트 페이지네이션 (기본 10개)"""
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArtistSearchAPIView(APIView):
    """🔍 아티스트 검색 API (이름, 부제목, 인물 기반 검색)"""
    pagination_class = ArtistPagination  

    def get(self, request):
        query = request.GET.get('q', '').strip()  # 🔍 검색어 (공백 제거)
        if len(query) < 2:
            return Response({"error": "두 글자 이상 입력해주세요."}, status=400)

        # 🔍 아티스트 검색 (이름, 부제목, 인물)
        artists = Artist.objects.filter(
            Q(title__icontains=query) | 
            Q(sub_titles__name__icontains=query) |
            Q(person__title__icontains=query),  # ✅ 참여 인물 검색 추가
            hide=False
        ).distinct()

        # 🔄 중복 제거 & 정렬 (인기순)
        artists = artists.annotate(
            weighted_score=F('like') * 0.8 + F('views') * 0.2
        ).order_by('-weighted_score')

        # 📌 페이지네이션 적용
        paginator = self.pagination_class()
        page_results = paginator.paginate_queryset(artists, request, view=self)

        if page_results is not None:
            serializer = ArtistSerializer(page_results, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response({"results": []})  # ✅ 빈 응답 방지
