from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import CreateView, DeleteView
from django.utils.decorators import method_decorator

from commentapp.forms import CommentCreationForm
from commentapp.models import Comment, Like, Dislike
from commentapp.decorators import comment_ownership_required

from django.http import JsonResponse
from django.views import View

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.contrib.contenttypes.models import ContentType


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentCreationForm
    template_name = 'commentapp/create.html'
    
    def form_valid(self, form):
        temp_comment = form.save(commit=False)
        # content_type과 object_id를 요청에서 가져옵니다.
        content_type_id = self.request.POST.get('content_type_id')
        content_type = get_object_or_404(ContentType, id=content_type_id)
        object_id = self.request.POST.get('object_id')
        model = content_type.model_class()  # 수정된 부분
        temp_comment.content_object = get_object_or_404(model, pk=object_id)
        temp_comment.writer = self.request.user
        temp_comment.save()
        self.object = temp_comment  # 성공 URL 메소드에서 사용
        return super().form_valid(form)
    
    def get_success_url(self):
        # 성공 URL을 동적으로 생성합니다.
        model = self.object.content_object._meta.model_name  # 수정된 부분
        app_label = self.object.content_object._meta.app_label  # 추가된 부분
        return reverse(f'{app_label}:detail', kwargs={'pk': self.object.object_id})
    
     
    
@method_decorator(comment_ownership_required, 'get')
@method_decorator(comment_ownership_required, 'post')
class CommentDeleteView(DeleteView):
    model = Comment
    context_object_name = 'target_comment'
    template_name = 'commentapp/delete.html'
    
    def get_success_url(self):
        # 삭제된 댓글이 연결된 객체의 타입과 ID를 기반으로 리디렉션 URL 결정
        content_type = self.object.content_type
        object_id = self.object.object_id
        
        # 앱 이름을 사용하여 URL name을 도출하고 리디렉션
        # 프로젝트의 URL 이름 패턴이 'detail'로 동일한 경우 사용
        app_label = content_type.app_label
        return reverse(f'{app_label}:detail', kwargs={'pk': object_id})

@login_required
def like_comment(request, comment_id):
     with transaction.atomic():
        if request.method == 'POST':
            comment = get_object_or_404(Comment, id=comment_id)
            liked = False  # 좋아요가 추가되었는지 여부를 추적
            like_qs = Like.objects.filter(user=request.user, comment=comment)

            if like_qs.exists():
                like_qs[0].delete()
            else:
                Like.objects.create(user=request.user, comment=comment)
                liked = True

            # 현재 좋아요의 총 개수
            total_likes = comment.likes.count()

            return JsonResponse({'liked': liked, 'total_likes': total_likes})
        else:
            return JsonResponse({'error': 'POST request required.'}, status=400)

@login_required
def dislike_comment(request, comment_id):
    with transaction.atomic():
        if request.method == 'POST':
            comment = get_object_or_404(Comment, id=comment_id)
            disliked = False  # 싫어요가 추가되었는지 여부를 추적
            dislike_qs = Dislike.objects.filter(user=request.user, comment=comment)

            if dislike_qs.exists():
                dislike_qs[0].delete()
            else:
                Dislike.objects.create(user=request.user, comment=comment)
                disliked = True

            # 현재 싫어요의 총 개수
            total_dislikes = comment.dislikes.count()

            return JsonResponse({'disliked': disliked, 'total_dislikes': total_dislikes})
        else:
            return JsonResponse({'error': 'POST request required.'}, status=400)

# --------------------------------comunity--------------------------------------------------------------------------------
