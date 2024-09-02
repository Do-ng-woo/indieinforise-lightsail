# forms.py
from django import forms
from django.forms import ModelForm, Textarea
from artistapp.models import Artist, Subtitle,Person

class ArtistCreationForm(forms.ModelForm):
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(기본적으로 Artist의 title을 입력해주세요)(쉼표로 구분)')

    class Meta:
        model = Artist
        fields = ['title', 'image']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        artist = super().save(commit=False)

        # Many-to-Many 필드를 처리하기 전에 먼저 Artist 인스턴스를 저장합니다.
        artist.save()

        # sub_titles_input 처리
        if self.cleaned_data.get('sub_titles_input'):
            sub_titles_list = self.cleaned_data['sub_titles_input']
            artist.sub_titles.clear()  # 기존 부제목 클리어
            for sub_title_name in sub_titles_list:
                subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                artist.sub_titles.add(subtitle)

        return artist


class ArtistUpdateForm(ModelForm):
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목')
    descriptions = forms.CharField(widget=forms.Textarea(attrs={'hidden': True}), required=False, label='설명')

    class Meta:            
        model = Artist
        fields = ['title', 'image','hide']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        artist = super().save(commit=False)

        # 기존 부제목을 클리어하고 새로운 부제목을 추가합니다.
        if self.cleaned_data.get('sub_titles_input', None):
            artist.sub_titles.clear()
            for sub_title_name in self.cleaned_data.get('sub_titles_input', []):
                subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                artist.sub_titles.add(subtitle)

        
        if commit:
            artist.save()

        return artist

    
class ArtistHotPointForm(forms.Form):
    points_to_use = forms.IntegerField(min_value=10, required=True)

    def clean_points_to_use(self):
        points = self.cleaned_data.get('points_to_use')
        if points % 10 != 0:
            raise forms.ValidationError('포인트는 10 단위로 사용해야 합니다.')
        return points