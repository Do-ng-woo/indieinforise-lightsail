from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

from articleapp.models import Article
from communityapp.models import Community
from artistapp.models import Artist
from personapp.models import Person
from projectapp.models import Project
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument

class LikeRecord(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like_recode')
    
    class Meta:
        unique_together = ('user','article')
        
class CommunityLikeRecord(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='like_record')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_like_record')
    
    class Meta:
        unique_together = ('user', 'community')
        
class ArtistLikeRecord(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artist_like_recode')
    
    class Meta:
        unique_together = ('user','artist')
        
class ProjectLikeRecord(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_like_recode')
    
    class Meta:
        unique_together = ('user','project')
        
class PersonLikeRecord(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='person_like_recode')
    
    class Meta:
        unique_together = ('user','person')

class SingLikeRecord(models.Model):
    sing = models.ForeignKey(Sing, on_delete=models.CASCADE, related_name='sing_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sing_like_recode')
    
    class Meta:
        unique_together = ('user','sing')

class AlbumLikeRecord(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='album_like_recode')
    
    class Meta:
        unique_together = ('user','album')
        
class GenreLikeRecord(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='genre_like_recode')
    
    class Meta:
        unique_together = ('user','genre')
        
class InstrumentLikeRecord(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='instrument_like_recode')    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instrument_like_recode')
    
    class Meta:
        unique_together = ('user','instrument')