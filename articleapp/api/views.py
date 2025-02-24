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
