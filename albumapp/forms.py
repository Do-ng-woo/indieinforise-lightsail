# forms.py
from django import forms
from django.forms import ModelForm, Textarea,TextInput,CheckboxSelectMultiple
from albumapp.models import Album, Subtitle
from artistapp.models import Artist
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
        
class AlbumCreationForm(forms.ModelForm):
    artist = forms.ModelMultipleChoiceField(queryset=Artist.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(widget=MediumEditorWidget(attrs={'placeholder': '가사를 입력해주세요'}), label='가사')
    datetime = forms.DateTimeField(
        widget=DateTimePickerInput(),
        required=False  # datetime 필드를 선택적으로 설정
    )
    class Meta:
        model = Album
        fields = ['title', 'image','artist','datetime','content']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        album = super().save(commit=False)
        album.save()

        if commit:
            # Many-to-Many 데이터 저장을 위해 save_m2m 호출
            # self.cleaned_data['artist'].save_m2m() 코드 제거 또는 수정
            self.instance.artist.set(self.cleaned_data['artist'])

            # sub_titles_input 처리
            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                album.sub_titles.clear()  # 기존 부제목 클리어
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    album.sub_titles.add(subtitle)

        return album

class AlbumUpdateForm(ModelForm):
    artist = forms.ModelMultipleChoiceField(queryset=Artist.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'django-select2'}))
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(
        widget=MediumEditorWidget(attrs={'placeholder': '가사를 입력해주세요'}),
        label='가사'
    )
    datetime = forms.DateTimeField(
        widget=DateTimePickerInput(),
        required=False  # datetime 필드를 선택적으로 설정
    )
    class Meta:
        model = Album
        fields = ['title', 'image', 'artist', 'datetime', 'content','hide']  # hide 필드 추가 album 에서만 hide필드가 있어야 동작함 이유는 공부 필요

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        album = super().save(commit=False)
        album.save()

        if commit:
            self.instance.artist.set(self.cleaned_data['artist'])

            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                album.sub_titles.clear()
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    album.sub_titles.add(subtitle)

        return album
    
class AlbumSearchForm(forms.Form):
    SEARCH_FIELDS = [
        ('title', '앨범명'),
        ('artist', '아티스트'),
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
