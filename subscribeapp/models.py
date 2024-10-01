from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person

class P_Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='P_subscripton')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='P_subscripton')
    
    class Meta:
        unique_together = ('user', 'project')

class A_Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='A_subscripton')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='A_subscripton')
    
    class Meta:
        unique_together = ('user', 'artist')

class Per_Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Per_subscripton')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='Per_subscripton')
    
    class Meta:
        unique_together = ('user', 'person')
        
        