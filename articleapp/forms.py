from django.forms import ModelForm, CheckboxSelectMultiple
from articleapp.models import Article
from projectapp.models import Project
from artistapp.models import Artist
from django import forms
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

class DateRangePickerInput(forms.DateInput):
    template_name = 'widgets/daterangepicker.html'
    class Media:
        css = {
            'all': ('css/daterangepicker.css',)  # DateRangePicker의 CSS 파일 경로
        }
        js = ('js/daterangepicker.js', 'js/moment.min.js')  # DateRangePicker의 JS 파일과 moment.js 파일 경로



class ArticleCreationForm(ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'editable text-start', 'style': 'height:auto'})
    )
    
    # Project 필드에서 hide=False 조건 추가
    project = forms.ModelMultipleChoiceField(
        queryset=Project.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'})
    )
    
    # Artist 필드에서 hide=False 조건 추가
    artist = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.filter(hide=False), 
        widget=Select2MultipleWidget(attrs={'class': 'django-select2'})
    )
    
    datetime = forms.DateTimeField(
        widget=DateTimePickerInput(),
        required=False  # datetime 필드를 선택적으로 설정
    )
    
    # Link 필드 추가
    link = forms.URLField(
        required=False,  # 필수 입력이 아니도록 설정
        widget=forms.URLInput(attrs={'placeholder': 'Link (선택 사항)', 'class': 'form-control'})
    )
    
    # RunningTime 필드 추가
    running_time = forms.IntegerField(
        required=False,  # 필수 입력이 아니도록 설정
        widget=forms.NumberInput(attrs={'placeholder': 'Running Time in minutes (선택 사항)', 'class': 'form-control'})
    )

    class Meta:
        model = Article
        fields = ['title', 'image', 'project', 'artist', 'content', 'datetime', 'link', 'running_time']
        
        
class ArticleSearchForm(forms.Form):
    SEARCH_FIELDS = [
        ('title', 'Title'),
        ('date', 'Date'),
        ('project', 'Stage'),
        ('artist', 'Artist'),
    ]

    search_field = forms.ChoiceField(
        choices=SEARCH_FIELDS, 
        required=False, 
        label='검색할 필드',
        widget=forms.Select(attrs={'class': 'search-field'})
    )
    search_keyword = forms.CharField(
        max_length=255, 
        required=False, 
        label='검색어',
        widget=forms.TextInput(attrs={'class': 'search-keyword'})
    )
    date_range = forms.DateField(
        widget=DateRangePickerInput(attrs={'class': 'date-range'}),
        required=False, 
        label='날짜 범위'
    )

    

