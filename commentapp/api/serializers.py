from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from commentapp.models import Comment, Like, Dislike
from accountapp.models import CustomUser  # 사용자 정보 포함

class LikeSerializer(serializers.ModelSerializer):
    """👍 댓글 좋아요 직렬화"""
    user = serializers.StringRelatedField()

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']

class DislikeSerializer(serializers.ModelSerializer):
    """👎 댓글 싫어요 직렬화"""
    user = serializers.StringRelatedField()

    class Meta:
        model = Dislike
        fields = ['id', 'user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    """💬 댓글 직렬화"""
    writer = serializers.StringRelatedField()  # 사용자 닉네임 반환
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()  # 모델 정보 포함

    class Meta:
        model = Comment
        fields = [
            'id', 'writer', 'content', 'created_at',
            'content_type', 'object_id', 'likes_count', 'dislikes_count'
        ]

    def get_likes_count(self, obj):
        """👍 좋아요 개수 반환"""
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        """👎 싫어요 개수 반환"""
        return obj.dislikes.count()

    def get_content_type(self, obj):
        """🔍 연결된 모델 정보 제공"""
        return obj.content_type.model  # 예: "article", "community"
