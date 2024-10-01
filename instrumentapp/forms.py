from django import forms
from django.forms import ModelForm, Textarea, TextInput
from instrumentapp.models import Instrument, Subtitle
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
        
class InstrumentCreationForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(widget=MediumEditorWidget(attrs={'placeholder': '악기 설명을 입력해주세요'}))

    class Meta:
        model = Instrument
        fields = ['title', 'image', 'sub_titles_input', 'content']

    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        instrument = super().save(commit=False)

        if commit:
            instrument.save()
            self.save_m2m()

            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                instrument.sub_titles.clear()
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    instrument.sub_titles.add(subtitle)
        else:
            instrument.save()

        return instrument

class InstrumentUpdateForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-class', 'style': 'width:100%;'}))
    sub_titles_input = forms.CharField(max_length=100, required=False, label='부제목(쉼표로 구분)')
    content = forms.CharField(widget=MediumEditorWidget(attrs={'placeholder': '악기 설명을 입력해주세요'}))

    class Meta:
        model = Instrument
        fields = ['title', 'image', 'sub_titles_input', 'content']
    
    def clean_sub_titles_input(self):
        sub_titles_input = self.cleaned_data.get('sub_titles_input')
        if sub_titles_input:
            sub_titles_list = [sub_title.strip() for sub_title in sub_titles_input.split(',')]
            return sub_titles_list
        else:
            return []

    def save(self, commit=True):
        instrument = super().save(commit=False)
        instrument.save()

        if commit:
            if self.cleaned_data.get('sub_titles_input'):
                sub_titles_list = self.cleaned_data['sub_titles_input']
                instrument.sub_titles.clear()
                for sub_title_name in sub_titles_list:
                    subtitle, created = Subtitle.objects.get_or_create(name=sub_title_name)
                    instrument.sub_titles.add(subtitle)

        return instrument
    
class InstrumentSearchForm(forms.Form):
    SEARCH_FIELDS = [
        ('title', '악기명'),
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
