from rest_framework import serializers
from artistapp.models import Artist, Subtitle, HonoraryEntry, Description, ArtistUpdateLog, ArtistPointLog
from personapp.models import Person

class SubtitleSerializer(serializers.ModelSerializer):
    """🎵 아티스트 서브 타이틀 직렬화"""
    class Meta:
        model = Subtitle
        fields = ['id', 'name']

class PersonSerializer(serializers.ModelSerializer):
    """👤 멤버(사람) 직렬화"""
    class Meta:
        model = Person
        fields = ['id', 'name', 'role']

class HonoraryEntrySerializer(serializers.ModelSerializer):
    """🏆 명예의 전당 기록 직렬화"""
    artist = serializers.StringRelatedField()
    quarter_display = serializers.SerializerMethodField()

    class Meta:
        model = HonoraryEntry
        fields = ['id', 'artist', 'year', 'quarter', 'quarter_display', 'frame_style', 'hot_point', 'rank', 'category']

    def get_quarter_display(self, obj):
        return obj.get_quarter_display()

class DescriptionSerializer(serializers.ModelSerializer):
    """📜 아티스트 추가 설명 직렬화"""
    class Meta:
        model = Description
        fields = ['id', 'name', 'text']

class ArtistUpdateLogSerializer(serializers.ModelSerializer):
    """📝 아티스트 수정 기록 직렬화"""
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = ArtistUpdateLog
        fields = ['id', 'updated_by', 'updated_at', 'update_description']

class ArtistPointLogSerializer(serializers.ModelSerializer):
    """💰 아티스트 포인트 기록 직렬화"""
    user = serializers.StringRelatedField()
    artist = serializers.StringRelatedField()

    class Meta:
        model = ArtistPointLog
        fields = ['id', 'user', 'artist', 'points_used', 'created_at']

class ArtistSerializer(serializers.ModelSerializer):
    """🎤 아티스트 직렬화"""
    writer = serializers.StringRelatedField()
    sub_titles = SubtitleSerializer(many=True, read_only=True)
    person = PersonSerializer(many=True, read_only=True)
    detailed_descriptions = DescriptionSerializer(many=True, read_only=True)
    honorary_entries = HonoraryEntrySerializer(many=True, read_only=True)
    update_logs = ArtistUpdateLogSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()  # 이미지 URL 변환

    class Meta:
        model = Artist
        fields = [
            'id', 'writer', 'title', 'sub_titles', 'image', 'description',
            'person', 'text_person', 'like', 'hot_point', 'views',
            'comment_count', 'created_at', 'hide', 'honorary_entries',
            'detailed_descriptions', 'update_logs'
        ]

    def get_image(self, obj):
        """🖼️ 아티스트 이미지 URL 반환"""
        if obj.image:
            return obj.image.url
        return "/media/default_artist_image.jpg"
