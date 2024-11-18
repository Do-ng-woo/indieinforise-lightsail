from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from articleapp.models import Article
from django.urls import path
from django.shortcuts import render, redirect
from django.db import transaction
from django import forms
from communityapp.models import Community  # Community 모델 추가

# Register your models here.
# admin.py
class EmptyImageFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
    title = _('Image empty')
    
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'image_empty'
    
    def lookups(self, request, model_admin):
        # This is where you define the values and their labels for the filter.
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )
    
    def queryset(self, request, queryset):
        # This is where you process the selected filter value and return the filtered queryset.
        if self.value() == 'Yes':
            return queryset.filter(image='')
        if self.value() == 'No':
            return queryset.exclude(image='')


class OrderByFilter(admin.SimpleListFilter):
    title = _('Order by')
    parameter_name = 'order_by'

    def lookups(self, request, model_admin):
        return (
            ('title_asc', _('Title (A-Z)')),
            ('title_desc', _('Title (Z-A)')),
            ('oldest', _('Oldest')),
            ('newest', _('Newest')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'title_asc':
            return queryset.order_by('title')
        if self.value() == 'title_desc':
            return queryset.order_by('-title')
        if self.value() == 'oldest':
            return queryset.order_by('created_at')
        if self.value() == 'newest':
            return queryset.order_by('-created_at')


class HiddenFilter(admin.SimpleListFilter):
    title = _('Hidden status')
    parameter_name = 'hidden'

    def lookups(self, request, model_admin):
        return (
            ('hidden', _('Hidden')),
            ('not_hidden', _('Not Hidden')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'hidden':
            return queryset.filter(hide=True)
        if self.value() == 'not_hidden':
            return queryset.filter(hide=False)

class MergeArticlesForm(forms.Form):
    """
    병합 작업을 위한 폼
    """
    article1 = forms.ModelChoiceField(
        queryset=Article.objects.all(),
        label="Article 1 (Target)",
        help_text="병합 결과로 남길 Article을 선택하세요."
    )
    article2 = forms.ModelChoiceField(
        queryset=Article.objects.all(),
        label="Article 2 (Source)",
        help_text="데이터를 병합하고 삭제할 Article을 선택하세요."
    )

class ArticleAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden','redirect_to_merge_articles']
    list_per_page = 1000  # 한 페이지에 100개씩 표시
    list_filter = (EmptyImageFilter, OrderByFilter, HiddenFilter,)  # Add the custom filters to the list_filter

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected articles as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected articles as not hidden"


    # 병합 페이지로 리다이렉트
    def redirect_to_merge_articles(self, request, queryset):
        """
        커스텀 병합 페이지로 리다이렉트
        """
        if queryset.count() != 2:
            self.message_user(request, "병합하려면 두 개의 Article을 선택해야 합니다.", level="error")
            return redirect('/admin/articleapp/article/')
        article_ids = ','.join(map(str, queryset.values_list('id', flat=True)))
        return redirect(f'merge-articles/{article_ids}/')

    redirect_to_merge_articles.short_description = "Redirect to merge articles page"

    def get_urls(self):
        """
        커스텀 URL 추가
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'merge-articles/<str:article_ids>/',
                self.admin_site.admin_view(self.merge_articles_view),
                name='merge-articles',
            ),
        ]
        return custom_urls + urls

    @transaction.atomic
    def merge_articles_view(self, request, article_ids):
        """
        병합 작업을 처리하는 뷰
        """
        article_ids = article_ids.split(',')
        try:
            if len(article_ids) != 2:
                raise ValueError("Invalid number of articles selected.")
            article1 = Article.objects.get(id=article_ids[0])
            article2 = Article.objects.get(id=article_ids[1])
        except (Article.DoesNotExist, ValueError):
            self.message_user(request, "잘못된 요청입니다. 유효한 Article을 선택하세요.", level="error")
            return redirect('/admin/articleapp/article/')

        if request.method == "POST":
            form = MergeArticlesForm(request.POST)
            if form.is_valid():
                article1 = form.cleaned_data['article1']
                article2 = form.cleaned_data['article2']

                self.perform_merge(article1, article2)
                self.message_user(request, f"'{article1.title}'로 병합 완료.")
                return redirect('/admin/articleapp/article/')
        else:
            form = MergeArticlesForm(initial={
                'article1': article1,
                'article2': article2,
            })

        return render(request, 'admin/merge_articles.html', {
            'form': form,
            'article1': article1,
            'article2': article2,
        })

    def perform_merge(self, article1, article2):
        """
        병합 작업 수행
        """
        # 1. Article 필드 병합
        article1.views += article2.views
        article1.like += article2.like
        article1.comment_count += article2.comment_count
        if not article1.image and article2.image:
            article1.image = article2.image
        if not article1.content and article2.content:
            article1.content = article2.content
        if not article1.date and article2.date:
            article1.date = article2.date
        if not article1.datetime and article2.datetime:
            article1.datetime = article2.datetime
        if not article1.link and article2.link:
            article1.link = article2.link
        if not article1.running_time and article2.running_time:
            article1.running_time = article2.running_time
        article1.save()

        # 2. M2M 관계 병합

        # Project 관계 병합
        for project in article2.project.all():
            article1.project.add(project)

        # Artist 관계 병합
        for artist in article2.artist.all():
            article1.artist.add(artist)

        # Person 관계 병합
        for person in article2.person.all():
            article1.person.add(person)

        # Community 관계 업데이트
        for community in Community.objects.filter(article=article2):
            community.article.remove(article2)
            community.article.add(article1)

        # 3. 병합 완료 후 article2 삭제
        article2.delete()

admin.site.register(Article, ArticleAdmin)