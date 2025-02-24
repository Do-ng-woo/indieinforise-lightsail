from rest_framework import serializers
from genreapp.models import Genre, Description
from artistapp.models import Artist
from singapp.models import Sing

class GenreSerializer(serializers.ModelSerializer):
    """📝 장르 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    artist = serializers.SerializerMethodField()
    beginning_song = serializers.SerializerMethodField()
    masterpiece_song = serializers.SerializerMethodField()
    origins = serializers.SerializerMethodField()
    subgenres = serializers.SerializerMethodField()
    derived_genres = serializers.SerializerMethodField()
    related_genres = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = [
            'id', 'writer', 'title', 'content', 'appearance_period', 'period',
            'artist', 'beginning_song', 'masterpiece_song',
            'origins', 'subgenres', 'derived_genres', 'related_genres',
            'like', 'views', 'comment_count', 'created_at', 'updated_at',
            'descriptions'
        ]

    def get_artist(self, obj):
        """🎤 관련된 Artist 리스트 반환 (이름, 이미지)"""
        return [{"id": artist.id, "title": artist.title, "image": artist.image.url if artist.image else None} for artist in obj.artist.all()]

    def get_beginning_song(self, obj):
        """🎶 관련된 시작곡 반환 (이름)"""
        return [{"id": song.id, "title": song.title} for song in obj.beginning_song.all()]

    def get_masterpiece_song(self, obj):
        """🎵 대표곡 반환 (이름)"""
        return [{"id": song.id, "title": song.title} for song in obj.masterpiece_song.all()]

    def get_origins(self, obj):
        """🌍 기원 장르 반환"""
        return [{"id": genre.id, "title": genre.title} for genre in obj.origins.all()]

    def get_subgenres(self, obj):
        """📌 하위 장르 반환"""
        return [{"id": genre.id, "title": genre.title} for genre in obj.subgenres.all()]

    def get_derived_genres(self, obj):
        """🔗 파생 장르 반환"""
        return [{"id": genre.id, "title": genre.title} for genre in obj.derived_genres.all()]

    def get_related_genres(self, obj):
        """🔄 관련 장르 반환"""
        return [{"id": genre.id, "title": genre.title} for genre in obj.related_genres.all()]

    def get_descriptions(self, obj):
        """📝 추가 정보 반환"""
        return [{"id": desc.id, "name": desc.name, "text": desc.text} for desc in obj.detailed_descriptions.all()]
