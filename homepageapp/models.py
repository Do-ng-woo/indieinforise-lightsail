from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.conf import settings
from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article


class Homepage(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='homepage', null=True)
    project = models.ManyToManyField(Project, related_name='homepage', blank=True)
    artist = models.ManyToManyField(Artist, related_name='homepage', blank=True)
    person = models.ManyToManyField(Person, related_name='homepage', blank=True)
    article = models.ManyToManyField(Article, related_name='homepage', blank=True)
    