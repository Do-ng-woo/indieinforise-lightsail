from rest_framework import serializers
from singapp.models import Sing, Description, SingUpdateLog

class SingSerializer(serializers.ModelSerializer):
    """🎵 곡(Sing) 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    sub_titles = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Sing
        fields = [
            'id', 'writer', 'title', 'image', 'content', 'datetime',
            'sub_titles', 'artists', 'descriptions',
            'like', 'views', 'comment_count',
            'created_at', 'updated_at', 'hide'
        ]
    
    def get_sub_titles(self, obj):
        """📌 곡의 부제목 리스트 반환"""
        return [subtitle.name for subtitle in obj.sub_titles.all()]
    
    def get_artists(self, obj):
        """🎤 참여 아티스트 목록 반환"""
        return [{"id": artist.id, "name": artist.title, "image": artist.image.url} for artist in obj.artist.all()]
    
    def get_descriptions(self, obj):
        """📝 곡 설명 반환"""
        return [{"id": desc.id, "name": desc.name, "text": desc.text} for desc in obj.detailed_descriptions.all()]
    
    def get_image(self, obj):
        """🎵 곡 이미지 URL 반환"""
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class SingUpdateLogSerializer(serializers.ModelSerializer):
    """📝 곡 업데이트 기록 직렬화"""
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = SingUpdateLog
        fields = ['id', 'updated_by', 'updated_at', 'update_description', 'hide']


class DescriptionSerializer(serializers.ModelSerializer):
    """📌 곡 상세 설명 직렬화"""
    class Meta:
        model = Description
        fields = ['id', 'sing', 'name', 'text']
