from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accountapp.models import FavoriteSearch
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from projectapp.models import Project
from artistapp.models import Artist
from personapp.models import Person
from articleapp.models import Article
from singapp.models import Sing
from albumapp.models import Album
from genreapp.models import Genre
from instrumentapp.models import Instrument
from django_select2.forms import Select2Widget


User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='사용자 이름', max_length=64)
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label=_("사용자 이름"), help_text=_("필수. 150자 이하. 문자, 숫자, @/./+/-/_ 만 사용 가능합니다."))
    password1 = forms.CharField(label=_("비밀번호"), widget=forms.PasswordInput, help_text=_("비밀번호는 적어도 8자 이상이어야 하며, 너무 일반적이거나 개인 정보와 비슷할 수 없습니다."))
    password2 = forms.CharField(label=_("비밀번호 확인"), widget=forms.PasswordInput, help_text=_("확인을 위해 위와 동일한 비밀번호를 입력하세요."))

    email = forms.EmailField(label=_("이메일"))
    gender = forms.ChoiceField(label=_("성별"), choices=[
        ('M', _('남성')),
        ('F', _('여성')),
        ('O', _('기타'))
    ])
    birth_date = forms.DateField(label=_("생년월일"), widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    nickname = forms.CharField(label=_("닉네임"))
    purpose_of_use = forms.CharField(label=_("사용 목적"), widget=forms.Textarea)
    image = forms.ImageField(label=_("프로필 이미지"), required=False)
    message = forms.CharField(label=_("메시지"), required=False)
    # 개인정보 처리방침 동의 필드 추가
    privacy_policy_agreement = forms.BooleanField(
        label=_("개인정보 처리방침에 동의합니다."),
        required=True,
        help_text=_("개인정보 처리방침을 읽고 동의합니다.")
    )
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + (
            'email', 'gender', 'birth_date', 'nickname', 'purpose_of_use', 
            'image', 'message'
        )

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다. 다른 닉네임을 선택해 주세요.")
        return nickname
    
class CustomUserUpdateForm(UserChangeForm):
    password = None  # 비밀번호 변경 필드를 제외합니다.

    username = forms.CharField(label=_("사용자 이름"), help_text=_("필수. 150자 이하. 문자, 숫자, @/./+/-/_ 만 사용 가능합니다."))
    email = forms.EmailField(label=_("이메일"))
    gender = forms.ChoiceField(label=_("성별"), choices=[
        ('M', _('남성')),
        ('F', _('여성')),
        ('O', _('기타'))
    ])
    birth_date = forms.DateField(label=_("생년월일"), widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    nickname = forms.CharField(label=_("닉네임"))
    purpose_of_use = forms.CharField(label=_("사용 목적"), widget=forms.Textarea)
    image = forms.ImageField(label=_("프로필 이미지"), required=False)
    message = forms.CharField(label=_("메시지"), required=False)
    
    # 개인정보 처리방침 동의 필드 추가
    privacy_policy_agreement = forms.BooleanField(
        label=_("개인정보 처리방침에 동의"),
        required=False
    )

    class Meta:
        model = User  # CustomUser 모델을 사용하도록 변경
        fields = [
            'username', 'email', 'gender', 'birth_date', 'nickname',
            'purpose_of_use', 'image', 'message', 'privacy_policy_agreement'
        ]

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        
        # 사용자의 기존 동의 여부에 따라 필드의 초기값 설정
        if self.instance and self.instance.privacy_policy_agreement:
            self.fields['privacy_policy_agreement'].initial = True
            # 이미 동의한 경우 수정할 수 없도록 비활성화
            self.fields['privacy_policy_agreement'].widget.attrs['disabled'] = True
        else:
            self.fields['privacy_policy_agreement'].initial = False

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=nickname).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다. 다른 닉네임을 선택해 주세요.")
        return nickname

    def clean_privacy_policy_agreement(self):
        # 비활성화된 경우 클린 단계에서 값을 가져오지 않으므로 동의한 상태를 그대로 반환
        if self.instance and self.instance.privacy_policy_agreement:
            return self.instance.privacy_policy_agreement
        return self.cleaned_data['privacy_policy_agreement']
    
class FavoriteSearchForm(forms.ModelForm):
    SEARCH_FIELD_CHOICES = [
        ('title', '제목'),
        ('project', '공연장'),
        ('artist', '아티스트'),
        ('person', '인물'),
        ('article', '공연'),
        ('sing', '노래'),
        ('album', '앨범'),
        ('genre', '장르'),
        ('instrument', '악기'),
        # 필요한 만큼 더 추가
    ]
    search_field = forms.ChoiceField(
        choices=SEARCH_FIELD_CHOICES,
        label='검색 필드',
        widget=forms.Select(attrs={'id': 'custom_search_field', 'class': 'FavoriteSearch-select'})
    )

    class Meta:
        model = FavoriteSearch
        fields = ['search_field', 'keyword']
        labels = {
            'search_field': '검색 필드',
            'keyword': '키워드'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        search_field_value = self.data.get('search_field') or self.initial.get('search_field')
        if search_field_value == 'title':
            self.fields['keyword'] = forms.CharField(label='키워드', max_length=255, widget=forms.TextInput(attrs={'id': 'id_add_keyword', 'class': 'FavoriteSearch-element-select'}))
        else:
            self.fields['keyword'] = forms.CharField(label='키워드', max_length=255, widget=Select2Widget(attrs={'class': 'django-select2 FavoriteSearch-element-select', 'id': 'id_add_keyword', 'style': 'width: 60%;'}))

    def clean(self):
        cleaned_data = super().clean()
        if self.user:
            existing_count = FavoriteSearch.objects.filter(user=self.user).count()
            if existing_count >= 16:
                self.add_error(None, "더이상 추가할 수 없습니다. 수정 후 추가를 진행해주세요.")
        return cleaned_data
    