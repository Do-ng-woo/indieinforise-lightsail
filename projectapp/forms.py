from django import forms
from django.forms import ModelForm, Textarea
from projectapp.models import Project, Subtitle

class ProjectCreationForm(ModelForm):
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')

    class Meta:
        model = Project
        fields = ['title', 'image', 'address']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        project = super().save(commit=False)

        # sub_titles_input 처리
        if commit:
            project.save()

        if self.cleaned_data.get('sub_titles_input'):
            sub_titles_list = self.cleaned_data['sub_titles_input']
            project.sub_titles.clear()  # 기존 부제목 클리어
            for sub_title_name in sub_titles_list:
                subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                project.sub_titles.add(subtitle)

        return project


class ProjectUpdateForm(ModelForm):
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    
    class Meta:
        model = Project
        fields = ['title', 'image', 'address']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        project = super().save(commit=False)

        # 기존 부제목을 클리어하고 새로운 부제목을 추가합니다.
        if self.cleaned_data.get('sub_titles_input'):
            project.sub_titles.clear()
            for sub_title_name in self.cleaned_data.get('sub_titles_input', []):
                subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                project.sub_titles.add(subtitle)

        if commit:
            project.save()

        return project