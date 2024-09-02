from django.forms import ModelForm
from django import forms
from commentapp.models import Comment


class CommentCreationForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': '댓글을 입력하세요...',
                'style': 'height: 150px;',  # 초기 높이를 100px로 설정
            }),
        }
        labels = {
            'content': '댓글',
        }

