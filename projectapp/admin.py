from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from projectapp.models import Project, Subtitle
from django.urls import path
from django.shortcuts import render, redirect
from django.db import transaction
from django import forms
from articleapp.models import Article
from communityapp.models import Community

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
        return queryset

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



class SubtitleAdmin(admin.ModelAdmin):
    actions = ['delete_selected_subtitles', 'delete_orphan_subtitles']
    list_per_page = 1000  # 한 페이지에 1000개씩 표시
    actions_on_top = True
    actions_on_bottom = True
    list_filter = (HiddenFilter,)

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

    def delete_orphan_subtitles(self, request, queryset):
        # 부모 없는 서브타이틀 필터링 및 삭제
        orphans = Subtitle.objects.filter(project__isnull=True)
        orphans_count = orphans.count()
        orphans.delete()
        self.message_user(request, f"Deleted {orphans_count} orphan subtitles.")
    delete_orphan_subtitles.short_description = "Delete orphan subtitles"

admin.site.register(Subtitle, SubtitleAdmin)



class MergeProjectsForm(forms.Form):
    """
    병합 작업을 위한 폼
    """
    project1 = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Project 1 (Target)",
        help_text="병합 결과로 남길 Project를 선택하세요."
    )
    project2 = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Project 2 (Source)",
        help_text="데이터를 병합하고 삭제할 Project를 선택하세요."
    )




class ProjectAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden','redirect_to_merge_projects']
    list_per_page = 100
    list_filter = ('hide',OrderByFilter, HiddenFilter,)  # 숨김 필터 추가

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected projects as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected projects as not hidden"

    # 병합 페이지로 리다이렉트
    def redirect_to_merge_projects(self, request, queryset):
        """
        커스텀 병합 페이지로 리다이렉트
        """
        if queryset.count() != 2:
            self.message_user(request, "병합하려면 두 개의 Project를 선택해야 합니다.", level="error")
            return redirect('/admin/projectapp/project/')
        project_ids = ','.join(map(str, queryset.values_list('id', flat=True)))
        return redirect(f'merge-projects/{project_ids}/')

    redirect_to_merge_projects.short_description = "Redirect to merge projects page"

    def get_urls(self):
        """
        커스텀 URL 추가
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'merge-projects/<str:project_ids>/',
                self.admin_site.admin_view(self.merge_projects_view),
                name='merge-projects',
            ),
        ]
        return custom_urls + urls

    @transaction.atomic
    def merge_projects_view(self, request, project_ids):
        """
        병합 작업을 처리하는 뷰
        """
        project_ids = project_ids.split(',')
        try:
            if len(project_ids) != 2:
                raise ValueError("Invalid number of projects selected.")
            project1 = Project.objects.get(id=project_ids[0])
            project2 = Project.objects.get(id=project_ids[1])
        except (Project.DoesNotExist, ValueError):
            self.message_user(request, "잘못된 요청입니다. 유효한 Project를 선택하세요.", level="error")
            return redirect('/admin/projectapp/project/')

        if request.method == "POST":
            form = MergeProjectsForm(request.POST)
            if form.is_valid():
                project1 = form.cleaned_data['project1']
                project2 = form.cleaned_data['project2']

                self.perform_merge(project1, project2)
                self.message_user(request, f"'{project1.title}'로 병합 완료.")
                return redirect('/admin/projectapp/project/')
        else:
            form = MergeProjectsForm(initial={
                'project1': project1,
                'project2': project2,
            })

        return render(request, 'admin/merge_projects.html', {
            'form': form,
            'project1': project1,
            'project2': project2,
        })

    def perform_merge(self, project1, project2):
        """
        병합 작업 수행
        """
        # 1. Project 필드 병합
        project1.like += project2.like
        project1.views += project2.views
        if not project1.description and project2.description:
            project1.description = project2.description
        if not project1.latitude and project2.latitude:
            project1.latitude = project2.latitude
        if not project1.longitude and project2.longitude:
            project1.longitude = project2.longitude
        if not project1.address and project2.address:
            project1.address = project2.address
        project1.save()

        # 2. M2M 관계 병합

        # Subtitle 관계 병합
        for subtitle in project2.sub_titles.all():
            project1.sub_titles.add(subtitle)

        # Article 관계 병합
        for article in Article.objects.filter(project=project2):
            article.project.remove(project2)
            article.project.add(project1)

        # Community 관계 병합
        for community in Community.objects.filter(project=project2):
            community.project.remove(project2)
            community.project.add(project1)

        # 3. 병합 완료 후 project2 삭제
        project2.delete()

admin.site.register(Project, ProjectAdmin)