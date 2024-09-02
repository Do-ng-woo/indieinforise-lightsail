from django import forms
from django.forms import ModelForm, Textarea
from projectapp.models import Project


class ProjectCreationForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'image','address']
        
class ProjectUpdateForm(ModelForm):
    
    class Meta:            
        model = Project
        fields = ['title', 'image', 'address']
    