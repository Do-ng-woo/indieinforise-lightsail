from django.forms import ModelForm, CheckboxSelectMultiple
from communityapp.models import Community
from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument
from django import forms
from django_select2.forms import Select2MultipleWidget


class DateRangePickerInput(forms.DateInput):
    template_name = 'widgets/daterangepicker.html'
    class Media:
        css = {
            'all': ('css/daterangepicker.css',)  # DateRangePicker의 CSS 파일 경로
        }
        js = ('js/daterangepicker.js', 'js/moment.min.js')  # DateRangePicker의 JS 파일과 moment.js 파일 경로

class TinyMCEWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {'class': 'editable tinymce text-start', 'style': 'height: 35rem'}
        super().__init__(*args, **kwargs)

class CommunityCreationForm(ModelForm):
    content = forms.CharField(widget=TinyMCEWidget())
    
    project = forms.ModelMultipleChoiceField(
        queryset=Project.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    artist = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    person = forms.ModelMultipleChoiceField(
        queryset=Person.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    article = forms.ModelMultipleChoiceField(
        queryset=Article.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    sing = forms.ModelMultipleChoiceField(
        queryset=Sing.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    album = forms.ModelMultipleChoiceField(
        queryset=Album.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    genre = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )
    instrument = forms.ModelMultipleChoiceField(
        queryset=Instrument.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'}), 
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        # 각 필드가 선택되지 않았다면 빈 리스트를 할당
        for field in ['project', 'artist', 'person', 'article', 'sing', 'album', 'genre', 'instrument']:
            if field not in cleaned_data or not cleaned_data[field]:
                cleaned_data[field] = []
        return cleaned_data
    
    class Meta:
        model = Community
        fields = ['board_type', 'image', 'title', 'content', 'article', 'person', 'sing', 'genre', 
                  'album', 'project', 'artist', 'instrument', 'hide']
        
        
class CommunitySearchForm(forms.Form):
    SEARCH_FIELDS = [
        ('title', '제목'),
        ('date', '날짜'),
        ('project', '공연장'),
        ('artist', '아티스트'),
        ('article','공연'),
        ('person','사람'),
        ('sing', '노래'),
        ('album', '앨범'),
        ('genre', '장르'),
        ('instrument', '악기')
    ]

    search_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'search-field'}),
        choices=SEARCH_FIELDS,
        required=False,
        label='검색할 필드'
    )
    search_keyword = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'search-keyword'}),
        max_length=255,
        required=False,
        label='검색어'
    )
    date_range = forms.DateField(
        widget=DateRangePickerInput(attrs={'class': 'date-range'}),
        required=False,
        label='날짜 범위'
    )

    

