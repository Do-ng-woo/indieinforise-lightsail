from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.list import MultipleObjectMixin
from allauth.account.models import EmailAddress  # EmailAddress 모델 가져오기

from accountapp.decorators import account_ownership_required
from accountapp.models import HelloWorld
from articleapp.models import Article
from communityapp.models import Community
from artistapp.models import Artist
from personapp.models import Person
from projectapp.models import Project
from singapp.models import Sing
from genreapp.models import Genre
from albumapp.models import Album
from instrumentapp.models import Instrument
from commentapp.models import Comment
from likeapp.models import LikeRecord,CommunityLikeRecord, ArtistLikeRecord, PersonLikeRecord, ProjectLikeRecord, SingLikeRecord, GenreLikeRecord, AlbumLikeRecord
from accountapp.forms import FavoriteSearchForm, CustomUserCreationForm, CustomUserUpdateForm
from accountapp.models import FavoriteSearch,EmailUser
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, DeleteView

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.crypto import get_random_string
from django.contrib.auth import login, get_backends


User = get_user_model()


has_ownership=[account_ownership_required, login_required]
@login_required
def hello_world(request):    
    
    if request.method == "POST":

        temp = request.POST.get('hello_world_input')

        new_hello_world = HelloWorld()
        new_hello_world.text = temp
        new_hello_world.save()

        hello_world_list = HelloWorld.objects.all()
        return HttpResponseRedirect(reverse('accountapp:hello_world'))
    else:
        hello_world_list = HelloWorld.objects.all()
        return render(request, 'accountapp/hello_world.html', context={'hello_world_list': hello_world_list})

def privacy_policy(request):
    return render(request, 'accountapp/privacy_policy.html')
    
class AccountCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('homepageapp:main')
    template_name = 'accountapp/create.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('homepageapp:main')
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        email_user = get_object_or_404(EmailUser, email=email)

        # 이메일 인증 여부 확인
        if not email_user.is_verified:
            form.add_error('email', '이메일 인증이 완료되지 않았습니다.')
            return self.form_invalid(form)

        # 새로운 사용자 생성
        response = super().form_valid(form)
        user = form.instance
        email_user.account_created = True  # 계정 생성 완료 상태로 업데이트
        email_user.save()

        # EmailAddress 모델에 이메일 추가
        EmailAddress.objects.create(
            user=user,
            email=email,
            verified=True,  # 기본적으로 True로 설정
            primary=True
        )

        # 개인정보 처리방침 동의 상태 저장
        privacy_policy_agreement_value = self.request.POST.get('privacy_policy_agreement')
        user.privacy_policy_agreement = privacy_policy_agreement_value == "on"
        user.save()

        # 사용자 로그인 처리
        backend = get_backends()[0]  # 첫 번째 인증 백엔드를 사용 (필요에 따라 다른 백엔드를 사용할 수도 있음)
        user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
        login(self.request, user)

        # 10분이 지난 인증되지 않은 EmailUser 객체 삭제 실행
        from django.core.management import call_command
        call_command('delete_expired_emailusers')

        return response

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    
@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountUpdateView(UpdateView):
    model = User
    context_object_name = 'target_user'
    form_class = CustomUserUpdateForm
    template_name = 'accountapp/update.html'
    success_url = reverse_lazy('articleapp:list')

    def form_valid(self, form):
        return super().form_valid(form)
    
    
class AccountDetailView(DetailView):
    model = User
    context_object_name = 'target_user'
    template_name = 'accountapp/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        view_type = self.request.GET.get('view_type', 'posts')  # 기본값은 'posts'
        content_type = self.request.GET.get('content_type', 'artist')  # 기본값은 'artist'

        content_type_labels = self.get_content_type_labels()
        detail_url_map = self.get_detail_url_map()
        detail_url = detail_url_map.get(content_type, 'communityapp:detail')

        objects = self.get_filtered_objects(view_type, content_type, user)

        # 댓글 수 카운트 및 전체 포스트 수 카운트
        total_posts_count = self.get_total_posts_count(user)
        comments_count = Comment.objects.filter(writer=user).count()

        # 페이지네이션 처리
        page = self.request.GET.get('page', 1)
        paginator = Paginator(objects, 12)
        context['objects'] = paginator.get_page(page)
        context['view_type'] = view_type
        context['content_type'] = content_type
        context['content_type_label'] = content_type_labels.get(content_type, content_type)
        context['total_posts_count'] = total_posts_count
        context['comments_count'] = comments_count
        context['detail_url'] = detail_url

        return context

    def get_content_type_labels(self):
        return {
            'artist': '아티스트',
            'article': '공연',
            'person': '인물',
            'project': '공연장',
            'sing': '노래',
            'album': '앨범',
            'genre': '장르',
            'community': '커뮤니티'
        }

    def get_detail_url_map(self):
        return {
            'artist': 'artistapp:detail',
            'article': 'articleapp:detail',
            'person': 'personapp:detail',
            'project': 'projectapp:detail',
            'sing': 'singapp:detail',
            'album': 'albumapp:detail',
            'genre': 'genreapp:detail',
            'community': 'communityapp:detail'
        }

    def get_filtered_objects(self, view_type, content_type, user):
        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        
        if view_type == 'posts':
            return model.objects.filter(writer=user, hide=False)
        elif view_type == 'drafts':
            return model.objects.filter(writer=user, hide=True)
        elif view_type == 'comments':
            return self.get_commented_objects(content_type, user)
        elif view_type == 'likes':
            return self.get_liked_objects(content_type, user)
        return model.objects.none()

    def get_commented_objects(self, content_type, user):
        comments = Comment.objects.filter(writer=user)
        content_type_ids = {}
        for comment in comments:
            ct = ContentType.objects.get_for_id(comment.content_type_id)
            if ct.model in content_type_ids:
                content_type_ids[ct.model].append(comment.object_id)
            else:
                content_type_ids[ct.model] = [comment.object_id]

        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        return model.objects.filter(pk__in=content_type_ids.get(content_type, []))

    def get_liked_objects(self, content_type, user):
        like_record_map = {
            'artist': ArtistLikeRecord,
            'article': LikeRecord,
            'person': PersonLikeRecord,
            'project': ProjectLikeRecord,
            'sing': SingLikeRecord,
            'album': AlbumLikeRecord,
            'genre': GenreLikeRecord,
            'community': CommunityLikeRecord
        }
        like_record = like_record_map.get(content_type, CommunityLikeRecord)
        liked_ids = like_record.objects.filter(user=user).values_list(content_type, flat=True)
        
        model_map = {
            'artist': Artist,
            'article': Article,
            'person': Person,
            'project': Project,
            'sing': Sing,
            'album': Album,
            'genre': Genre,
            'community': Community
        }
        model = model_map.get(content_type, Community)
        return model.objects.filter(pk__in=liked_ids).distinct()

    def get_total_posts_count(self, user):
        return Artist.objects.filter(writer=user).count() + \
               Article.objects.filter(writer=user).count() + \
               Project.objects.filter(writer=user).count() + \
               Person.objects.filter(writer=user).count() + \
               Community.objects.filter(writer=user).count() + \
               Sing.objects.filter(writer=user).count() + \
               Album.objects.filter(writer=user).count() + \
               Genre.objects.filter(writer=user).count()


    


@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountDeleteView(DeleteView):
    model = User
    context_object_name = 'target_user'
    success_url = reverse_lazy('accountapp:login')
    template_name = 'accountapp/delete.html'
    

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accountapp/login.html'

    def dispatch(self, request, *args, **kwargs):
        # 사용자가 로그인 상태인지 확인
        if request.user.is_authenticated:
            # 로그인되어 있으면 메인 페이지로 리다이렉트
            return redirect('homepageapp:main')  # 원하는 URL로 리다이렉트
        # 로그인되어 있지 않으면 원래대로 dispatch 진행
        return super().dispatch(request, *args, **kwargs)
    
    
# ======================================================================================
def add_favorite_search(request):
    if request.method == 'POST':
        form = FavoriteSearchForm(request.POST, user=request.user)
        if form.is_valid():
            favorite_search = form.save(commit=False)
            favorite_search.user = request.user
            existing_count = FavoriteSearch.objects.filter(user=request.user).count()
            if existing_count < 8:
                try:
                    favorite_search.save()
                    messages.success(request, "즐겨찾는 키워드가 추가되었습니다")
                    return redirect(reverse('communityapp:list'))
                except IntegrityError:
                    messages.warning(request, "이미 같은 즐겨찾기 키워드가 존재합니다.")
            else:
                messages.warning(request, "더이상 추가할 수 없습니다. 수정 후 추가를 진행해주세요.")
        else:
            # 특정 에러 메시지를 폼에서 가져와서 메시지로 추가
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.warning(request, error)
            else:
                messages.warning(request, "입력 값이 유효하지 않습니다. 다시 시도해주세요.")
    else:
        form = FavoriteSearchForm(user=request.user)

    return redirect(reverse('communityapp:list'))

def delete_favorite_keyword(request, keyword_id):
    keyword = FavoriteSearch.objects.get(id=keyword_id, user=request.user)
    keyword.delete()
    messages.success(request, "즐겨찾는 키워드가 삭제되었습니다.")
    return redirect(reverse('communityapp:list'))

def get_field_data(request):
    field = request.GET.get('field')
    data = []
    
    if field == 'artist':
        data = list(Artist.objects.filter(hide=False).values('id', 'title'))
    elif field == 'project':
        data = list(Project.objects.filter(hide=False).values('id', 'title'))
    elif field == 'person':
        data = list(Person.objects.filter(hide=False).values('id', 'title'))
    elif field == 'article':
        data = list(Article.objects.filter(hide=False).values('id', 'title'))
    elif field == 'sing':
        data = list(Sing.objects.filter(hide=False).values('id', 'title'))
    elif field == 'album':
        data = list(Album.objects.filter(hide=False).values('id', 'title'))
    elif field == 'genre':
        data = list(Genre.objects.filter(hide=False).values('id', 'title'))
    elif field == 'instrument':
        data = list(Instrument.objects.filter(hide=False).values('id', 'title'))

    return JsonResponse(data, safe=False)


@csrf_exempt
def send_verification_email_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if email:
                # EmailUser 모델에서 해당 이메일이 이미 존재하는지 확인
                email_user, created = EmailUser.objects.get_or_create(email=email)

                if not created and email_user.is_verified:
                    return JsonResponse({'success': False, 'error': '이미 인증된 이메일입니다. 그냥 진행할 수 있습니다.'})

                # User 모델에서 해당 이메일을 가진 사용자가 있는지 확인 (중복된 계정 생성 방지)
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'success': False, 'error': '이미 가입된 이메일입니다.'})

                # 이메일 인증에 필요한 토큰 및 UID 생성 (임시 방식으로 처리)
                token = get_random_string(20)  # 인증에 사용할 임시 토큰
                uid = urlsafe_base64_encode(force_bytes(email_user.pk))

                # 이메일 전송
                success = send_verification_email(email, token, uid)

                if success:
                    # 토큰을 저장해 인증 단계에서 비교할 수 있도록 처리
                    email_user.token = token
                    email_user.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': '이메일 전송에 실패했습니다. 다시 시도해주세요.'})

            else:
                return JsonResponse({'success': False, 'error': '유효한 이메일이 아닙니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': '유효하지 않은 요청입니다.'})

def send_verification_email(email, token, uid):
    subject = '이메일 인증을 완료해주세요'
    message = f'회원가입을 완료하려면 다음 링크를 클릭해주세요: https://indieboost.co.kr/accounts/activate/{uid}/{token}/'

    try:
        send_mail(
            subject,
            message,
            'indieboostkorea@gmail.com',  # 발신자 이메일
            [email],  # 수신자 이메일
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"이메일 전송 실패: {str(e)}")
        return False

def activate_account(request, uidb64, token):
    try:
        # UID를 사용해 EmailUser 객체를 복호화하고 검색
        uid = urlsafe_base64_decode(uidb64).decode()
        email_user = get_object_or_404(EmailUser, pk=uid)

        # 토큰이 유효한지 확인
        if email_user.token == token:
            # 이메일 인증 완료
            email_user.is_verified = True
            email_user.save()
            return render(request, 'accountapp/activation_success.html', {
                'message': '이메일 인증이 성공적으로 완료되었습니다.'
            })
        else:
            return render(request, 'accountapp/activation_failure.html', {
                'message': '유효하지 않은 링크입니다.'
            })
    except Exception as e:
        return render(request, 'accountapp/activation_failure.html', {
            'message': f'오류가 발생했습니다: {str(e)}'
        })