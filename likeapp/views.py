from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction

from articleapp.models import Article
from artistapp.models import Artist
from communityapp.models import Community
from personapp.models import Person
from projectapp.models import Project
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument
from likeapp.models import LikeRecord
from likeapp.models import CommunityLikeRecord, ArtistLikeRecord, PersonLikeRecord, ProjectLikeRecord, SingLikeRecord, AlbumLikeRecord, GenreLikeRecord, InstrumentLikeRecord


@transaction.atomic
def db_transaction(user, article):
    if LikeRecord.objects.filter(user=user, article=article).exists():
        raise ValidationError('Like already exists')            
    else:
        LikeRecord(user=user, article=article).save()

    article.like += 1
    article.save()
       

@method_decorator(login_required,'get')
class LikeArticleView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('articleapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        article = get_object_or_404(Article, pk=kwargs['pk'])
        
        try:
            db_transaction(user, article)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('articleapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeArticleView, self).get(self.request, *args, **kwargs)
# -------------------------------------------------------------------------------커뮤니티 앱 -----------------------------------------------------------------------------------------
@transaction.atomic
def Community_db_transaction(user, community):
    if CommunityLikeRecord.objects.filter(user=user, community=community).exists():
        raise ValidationError('Like already exists')            
    else:
        CommunityLikeRecord(user=user, community=community).save()

    community.like += 1
    community.save()
       

@method_decorator(login_required,'get')
class LikeCommunityView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('communityapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        community = get_object_or_404(Community, pk=kwargs['pk'])
        
        try:
            Community_db_transaction(user, community)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('communityapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeCommunityView, self).get(self.request, *args, **kwargs)
    

# ---------------------------------------------------------------------------------------------------------
@transaction.atomic
def Artist_db_transaction(user, artist):
    if ArtistLikeRecord.objects.filter(user=user, artist=artist).exists():
        raise ValidationError('Like already exists')            
    else:
        ArtistLikeRecord(user=user, artist=artist).save()

    artist.like += 1
    artist.save()
       

@method_decorator(login_required,'get')
class LikeArtistView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('artistapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        artist = get_object_or_404(Artist, pk=kwargs['pk'])
        
        try:
            Artist_db_transaction(user, artist)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('artistapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeArtistView, self).get(self.request, *args, **kwargs)

# -------------person-----------------------------------

@transaction.atomic
def Person_db_transaction(user, person):
    if PersonLikeRecord.objects.filter(user=user, person=person).exists():
        raise ValidationError('Like already exists')            
    else:
        PersonLikeRecord(user=user, person=person).save()

    person.like += 1
    person.save()
       

@method_decorator(login_required,'get')
class LikePersonView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('personapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        person = get_object_or_404(Person, pk=kwargs['pk'])
        
        try:
            Person_db_transaction(user, person)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('personapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikePersonView, self).get(self.request, *args, **kwargs)


# -------------------project------------------------------------------

@transaction.atomic
def Project_db_transaction(user, project):
    if ProjectLikeRecord.objects.filter(user=user, project=project).exists():
        raise ValidationError('Like already exists')            
    else:
        ProjectLikeRecord(user=user, project=project).save()

    project.like += 1
    project.save()
       

@method_decorator(login_required,'get')
class LikeProjectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('projectapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        project = get_object_or_404(Project, pk=kwargs['pk'])
        
        try:
            Project_db_transaction(user, project)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('projectapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeProjectView, self).get(self.request, *args, **kwargs)

# -------------------------------------------sing-----------------------------
@transaction.atomic
def Sing_db_transaction(user, sing):
    if SingLikeRecord.objects.filter(user=user, sing=sing).exists():
        raise ValidationError('Like already exists')            
    else:
        SingLikeRecord(user=user, sing=sing).save()

    sing.like += 1
    sing.save()
       

@method_decorator(login_required,'get')
class LikeSingView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('singapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        sing = get_object_or_404(Sing, pk=kwargs['pk'])
        
        try:
            Sing_db_transaction(user, sing)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('singapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeSingView, self).get(self.request, *args, **kwargs)
    
# -------------------------------------------album-----------------------------
@transaction.atomic
def Album_db_transaction(user, album):
    if AlbumLikeRecord.objects.filter(user=user, album=album).exists():
        raise ValidationError('Like already exists')            
    else:
        AlbumLikeRecord(user=user, album=album).save()

    album.like += 1
    album.save()
       

@method_decorator(login_required,'get')
class LikeAlbumView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('albumapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        album = get_object_or_404(Album, pk=kwargs['pk'])
        
        try:
            Album_db_transaction(user, album)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('albumapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeAlbumView, self).get(self.request, *args, **kwargs)
    
# -------------------------------------------genre-----------------------------
@transaction.atomic
def Genre_db_transaction(user, genre):
    if GenreLikeRecord.objects.filter(user=user, genre=genre).exists():
        raise ValidationError('Like already exists')            
    else:
        GenreLikeRecord(user=user, genre=genre).save()

    genre.like += 1
    genre.save()
       

@method_decorator(login_required,'get')
class LikeGenreView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('genreapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        genre = get_object_or_404(Genre, pk=kwargs['pk'])
        
        try:
            Genre_db_transaction(user, genre)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('genreapp:detail', kwargs={'pk':kwargs['pk']}))
            
        
        return super(LikeGenreView, self).get(self.request, *args, **kwargs)
    
#------------------------------instrument    
@transaction.atomic
def Instrument_db_transaction(user, instrument):
    if InstrumentLikeRecord.objects.filter(user=user, instrument=instrument).exists():
        raise ValidationError('Like already exists')            
    else:
        InstrumentLikeRecord(user=user, instrument=instrument).save()

    instrument.like += 1
    instrument.save()

@method_decorator(login_required, 'get')
class LikeInstrumentView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('instrumentapp:detail', kwargs={'pk': kwargs['pk']})
    
    def get(self, *args, **kwargs):
        
        user = self.request.user
        instrument = get_object_or_404(Instrument, pk=kwargs['pk'])
        
        try:
            Instrument_db_transaction(user, instrument)
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다')
            return HttpResponseRedirect(reverse('instrumentapp:detail', kwargs={'pk':kwargs['pk']}))
        
        return super(LikeInstrumentView, self).get(self.request, *args, **kwargs)
    