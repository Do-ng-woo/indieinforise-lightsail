from rest_framework import serializers
from communityapp.models import Community
from articleapp.models import Article
from artistapp.models import Artist
from projectapp.models import Project
from albumapp.models import Album
from singapp.models import Sing
from genreapp.models import Genre
from instrumentapp.models import Instrument
from personapp.models import Person

class CommunitySerializer(serializers.ModelSerializer):
    """📝 커뮤니티 게시글 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    article = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    sing = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    instrument = serializers.SerializerMethodField()
    person = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            'id', 'writer', 'title', 'image', 'content', 'created_at', 'date', 'datetime',
            'like', 'views', 'comment_count', 'board_type', 
            'article', 'project', 'artist', 'album', 'sing', 'genre', 'instrument', 'person'
        ]

    def get_article(self, obj):
        """🎟️ 연결된 Article 리스트 반환 (제목, 이미지)"""
        return [{"id": article.id, "title": article.title, "image": article.image.url if article.image else None} for article in obj.article.all()]

    def get_project(self, obj):
        """🏢 연결된 Project 리스트 반환 (이름, 이미지)"""
        return [{"id": project.id, "title": project.title, "image": project.image.url if project.image else None} for project in obj.project.all()]

    def get_artist(self, obj):
        """🎤 연결된 Artist 리스트 반환 (이름, 이미지)"""
        return [{"id": artist.id, "title": artist.title, "image": artist.image.url if artist.image else None} for artist in obj.artist.all()]

    def get_album(self, obj):
        """💿 연결된 Album 리스트 반환 (이름, 이미지)"""
        return [{"id": album.id, "title": album.title, "image": album.image.url if album.image else None} for album in obj.album.all()]

    def get_sing(self, obj):
        """🎶 연결된 Sing 리스트 반환 (이름)"""
        return [{"id": sing.id, "title": sing.title} for sing in obj.sing.all()]

    def get_genre(self, obj):
        """🎼 연결된 Genre 리스트 반환 (이름)"""
        return [{"id": genre.id, "title": genre.name} for genre in obj.genre.all()]

    def get_instrument(self, obj):
        """🎸 연결된 Instrument 리스트 반환 (이름)"""
        return [{"id": instrument.id, "title": instrument.name} for instrument in obj.instrument.all()]

    def get_person(self, obj):
        """👤 연결된 Person 리스트 반환 (이름)"""
        return [{"id": person.id, "title": person.name} for person in obj.person.all()]
