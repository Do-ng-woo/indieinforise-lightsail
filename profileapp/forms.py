from django.forms import ModelForm
from profileapp.models import Profile
from django import forms

class ProfileCreationForm(ModelForm):
    class Meta:
        model = Profile
        fields =['image', 'message']
        