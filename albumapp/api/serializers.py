from rest_framework import serializers
from albumapp.models import Album, Subtitle, Description, AlbumUpdateLog
from artistapp.models import Artist
from singapp.models import Sing

class SubtitleSerializer(serializers.ModelSerializer):
    """🎵 앨범 서브 타이틀 직렬화"""
    class Meta:
        model = Subtitle
        fields = ['id', 'name']

class ArtistSerializer(serializers.ModelSerializer):
    """🎤 아티스트 직렬화"""
    class Meta:
        model = Artist
        fields = ['id', 'title', 'image']

class SingSerializer(serializers.ModelSerializer):
    """🎶 수록곡 직렬화"""
    class Meta:
        model = Sing
        fields = ['id', 'title', 'duration']

class DescriptionSerializer(serializers.ModelSerializer):
    """📜 앨범 추가 설명 직렬화"""
    class Meta:
        model = Description
        fields = ['id', 'name', 'text']

class AlbumUpdateLogSerializer(serializers.ModelSerializer):
    """📌 앨범 수정 로그 직렬화"""
    updated_by = serializers.StringRelatedField()  # 업데이트한 사용자 이름 반환

    class Meta:
        model = AlbumUpdateLog
        fields = ['id', 'updated_by', 'updated_at', 'update_description']

class AlbumSerializer(serializers.ModelSerializer):
    """💿 앨범 직렬화"""
    artist = ArtistSerializer(many=True, read_only=True)
    sing = SingSerializer(many=True, read_only=True)
    sub_titles = SubtitleSerializer(many=True, read_only=True)
    detailed_descriptions = DescriptionSerializer(many=True, read_only=True)
    update_logs = AlbumUpdateLogSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()  # 이미지 URL 처리

    class Meta:
        model = Album
        fields = [
            'id', 'writer', 'title', 'sub_titles', 'image', 'content', 'datetime',
            'artist', 'sing', 'text_sing', 'like', 'views', 'comment_count',
            'created_at', 'updated_at', 'hide', 'detailed_descriptions', 'update_logs'
        ]

    def get_image(self, obj):
        """🖼️ 앨범 커버 이미지 URL 반환"""
        if obj.image:
            return obj.image.url
        return "/media/default_album_cover.jpg"
