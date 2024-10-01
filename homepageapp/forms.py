from django.forms import ModelForm, CheckboxSelectMultiple
from articleapp.models import Article
from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from homepageapp.models import Homepage
from django import forms
from django_select2.forms import Select2MultipleWidget

class HomepageCreationForm(ModelForm):    
    project = forms.ModelMultipleChoiceField(queryset=Project.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    artist = forms.ModelMultipleChoiceField(queryset=Artist.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    person = forms.ModelMultipleChoiceField(queryset=Person.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    

    
    class Meta:
        model = Homepage
        fields = ['project', 'artist','article','person']