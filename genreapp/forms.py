# forms.py
from django import forms
from django.forms import ModelForm, Textarea,TextInput,CheckboxSelectMultiple
from genreapp.models import Genre, Subtitle
from artistapp.models import Artist
from singapp.models import Sing
from django_select2.forms import Select2MultipleWidget

class DateTimePickerInput(forms.DateTimeInput):
    template_name = 'widgets/datetimepicker.html'

    class Media:
        css = {
            'all': ('css/jquery.datetimepicker.min.css',)  # DateTimePicker의 CSS 파일 경로
        }
        js = ('js/jquery.datetimepicker.full.min.js',)  # jQuery 및 DateTimePicker의 JS 파일 경로

    def __init__(self, attrs=None, format='%Y-%m-%d %H:%M'):  # 형식을 '%Y/%m/%d %H:%M'으로 설정
        super().__init__(attrs={'class': 'datetimepicker', **(attrs or {})}, format=format)

class MediumEditorWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        default_attrs = {'class': 'editable', 'style': 'height: 35rem; overflow-y: auto;'}
        if 'attrs' in kwargs:
            default_attrs.update(kwargs['attrs'])
        kwargs['attrs'] = default_attrs
        super().__init__(*args, **kwargs)

    class Media:
        css = {
            'all': ('//cdn.jsdelivr.net/npm/medium-editor@5.23.2/dist/css/medium-editor.min.css',)
        }
        js = ('//cdn.jsdelivr.net/npm/medium-editor@5.23.2/dist/js/medium-editor.min.js',)
        
class GenreCreationForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    appearance_period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    artist = forms.ModelMultipleChoiceField(queryset=Artist.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    beginning_song = forms.ModelMultipleChoiceField(queryset=Sing.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    masterpiece_song = forms.ModelMultipleChoiceField(queryset=Sing.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    origins = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    subgenres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    derived_genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    related_genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(widget=MediumEditorWidget(attrs={'placeholder': '가사를 입력해주세요'}))
    
    class Meta:
        model = Genre
        fields = ['title','appearance_period','period','artist','beginning_song','masterpiece_song','origins','subgenres','derived_genres','related_genres','content']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        genre = super().save(commit=False)

        # ManyToManyField 데이터 처리를 위해 임시 저장
        if commit:
            genre.save()
            self.save_m2m()  # 이 부분을 추가합니다.

            genre.artist.set(self.cleaned_data['artist'])
            genre.beginning_song.set(self.cleaned_data['beginning_song'])
            genre.masterpiece_song.set(self.cleaned_data['masterpiece_song'])
            genre.origins.set(self.cleaned_data['origins'])
            genre.subgenres.set(self.cleaned_data['subgenres'])
            genre.derived_genres.set(self.cleaned_data['derived_genres'])
            genre.related_genres.set(self.cleaned_data['related_genres'])

            # sub_titles_input 처리
            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                genre.sub_titles.clear()  # 기존 부제목 클리어
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    genre.sub_titles.add(subtitle)

        else:
            genre.save()

        return genre

class GenreUpdateForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    appearance_period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    artist = forms.ModelMultipleChoiceField(queryset=Artist.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    beginning_song = forms.ModelMultipleChoiceField(queryset=Sing.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    masterpiece_song = forms.ModelMultipleChoiceField(queryset=Sing.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    origins = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    subgenres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    derived_genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    related_genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.filter(hide=False), widget=Select2MultipleWidget(attrs={'class': 'django-select2','style': 'width:100%;'}),required=False)
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(widget=MediumEditorWidget(attrs={'placeholder': '가사를 입력해주세요'}))
    
    class Meta:
        model = Genre
        fields = ['title','appearance_period','period','artist','beginning_song','masterpiece_song','origins','subgenres','derived_genres','related_genres','content']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        genre = super().save(commit=False)
        genre.save()

        if commit:
            # Many-to-Many 데이터 저장을 위해 save_m2m 호출
            # self.cleaned_data['artist'].save_m2m() 코드 제거 또는 수정
            self.instance.artist.set(self.cleaned_data['artist'])

            # sub_titles_input 처리
            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                genre.sub_titles.clear()  # 기존 부제목 클리어
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    genre.sub_titles.add(subtitle)

        return genre
    
class GenreSearchForm(forms.Form):
    SEARCH_FIELDS = [
        ('title', '장르명'),
    ]
    search_field = forms.ChoiceField(
        choices=SEARCH_FIELDS, 
        required=False, 
        label='검색할 필드',
        widget=forms.Select(attrs={'class': 'sing-search-field'})
    )
    search_keyword = forms.CharField(
        max_length=255, 
        required=False, 
        label='검색어',
        widget=forms.TextInput(attrs={'class': 'sing-search-keyword'})
    )
    
