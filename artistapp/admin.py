from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from artistapp.models import Artist, Subtitle, Description, HonoraryEntry
from django.urls import path
from django.shortcuts import render, redirect
from django.db import transaction
from django import forms

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
    list_per_page = 100  # 한 페이지에 1000개씩 표시
    actions_on_top = True
    actions_on_bottom = True
    list_filter = (HiddenFilter,)

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

    def delete_orphan_subtitles(self, request, queryset):
        # 부모 없는 서브타이틀 필터링 및 삭제
        orphans = Subtitle.objects.filter(artists__isnull=True)
        orphans_count = orphans.count()
        orphans.delete()
        self.message_user(request, f"Deleted {orphans_count} orphan subtitles.")
    delete_orphan_subtitles.short_description = "Delete orphan subtitles"

admin.site.register(Subtitle, SubtitleAdmin)

class DescriptionAdmin(admin.ModelAdmin):
    actions = ['delete_selected_description']
    list_filter = (HiddenFilter,)

    def delete_selected_description(self, request, queryset):
        queryset.delete()
    delete_selected_description.short_description = "Delete selected description"

admin.site.register(Description, DescriptionAdmin)


class HonoraryEntryAdmin(admin.ModelAdmin):
    list_display = ('artist', 'year', 'quarter', 'hot_point', 'rank', 'category', 'frame_style')
    list_filter = ('year', 'quarter', 'category')
    search_fields = ('artist__title',)

admin.site.register(HonoraryEntry, HonoraryEntryAdmin)



class MergeArtistsForm(forms.Form):
    """
    병합 작업을 위한 폼
    """
    artist1 = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        label="Artist 1 (Target)",
        help_text="병합 결과로 남길 아티스트를 선택하세요."
    )
    artist2 = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        label="Artist 2 (Source)",
        help_text="데이터를 병합하고 삭제할 아티스트를 선택하세요."
    )
    new_title = forms.CharField(
        max_length=200,
        label="New Title",
        required=False,
        help_text="새로운 제목을 입력하거나 Artist 1의 제목을 그대로 사용합니다."
    )
class MergeArtistsForm(forms.Form):
    """
    병합 작업을 위한 폼
    """
    artist1 = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        label="Artist 1 (Target)",
        help_text="병합 결과로 남길 아티스트를 선택하세요."
    )
    artist2 = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        label="Artist 2 (Source)",
        help_text="데이터를 병합하고 삭제할 아티스트를 선택하세요."
    )
    new_title = forms.CharField(
        max_length=200,
        label="New Title",
        required=False,
        help_text="새로운 제목을 입력하거나 Artist 1의 제목을 그대로 사용합니다."
    )

class ArtistAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden', 'redirect_to_merge_artists']
    list_per_page = 100
    list_filter = ('hide',)  # 숨김 필터 추가

    # 숨김 처리
    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected artists as hidden"

    # 숨김 해제
    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected artists as not hidden"

    # 병합 페이지로 리다이렉트
    def redirect_to_merge_artists(self, request, queryset):
        """
        커스텀 병합 페이지로 리다이렉트
        """
        if queryset.count() != 2:
            self.message_user(request, "병합하려면 두 개의 아티스트를 선택해야 합니다.", level="error")
            return redirect('/admin/artistapp/artist/')
        artist_ids = ','.join(map(str, queryset.values_list('id', flat=True)))
        return redirect(f'merge-artists/{artist_ids}/')

    redirect_to_merge_artists.short_description = "Redirect to merge artists page"

    def get_urls(self):
        """
        커스텀 URL 추가
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'merge-artists/<str:artist_ids>/',
                self.admin_site.admin_view(self.merge_artists_view),
                name='merge-artists',
            ),
        ]
        return custom_urls + urls

    @transaction.atomic
    def merge_artists_view(self, request, artist_ids):
        """
        병합 작업을 처리하는 뷰
        """
        artist_ids = artist_ids.split(',')
        try:
            if len(artist_ids) != 2:
                raise ValueError("Invalid number of artists selected.")
            artist1 = Artist.objects.get(id=artist_ids[0])
            artist2 = Artist.objects.get(id=artist_ids[1])
        except (Artist.DoesNotExist, ValueError):
            self.message_user(request, "잘못된 요청입니다. 유효한 아티스트를 선택하세요.", level="error")
            return redirect('/admin/artistapp/artist/')

        if request.method == "POST":
            form = MergeArtistsForm(request.POST)
            if form.is_valid():
                artist1 = form.cleaned_data['artist1']
                artist2 = form.cleaned_data['artist2']
                new_title = form.cleaned_data['new_title']

                self.perform_merge(artist1, artist2, new_title)
                self.message_user(request, f"'{artist1.title}'로 병합 완료.")
                return redirect('/admin/artistapp/artist/')
        else:
            form = MergeArtistsForm(initial={
                'artist1': artist1,
                'artist2': artist2,
            })

        return render(request, 'admin/merge_artists.html', {
            'form': form,
            'artist1': artist1,
            'artist2': artist2,
        })

    def perform_merge(self, artist1, artist2, new_title=None):
        """
        병합 작업 수행
        """
        # 1. Artist 필드 병합
        artist1.like += artist2.like
        artist1.views += artist2.views
        artist1.hot_point += artist2.hot_point
        artist1.comment_count += artist2.comment_count
        if new_title:
            artist1.title = new_title
        artist1.save()

        # 2. M2M 관계 병합

        # Sing 관계 업데이트
        for sing in artist2.sing.all():
            sing.artist.remove(artist2)
            sing.artist.add(artist1)

        # Subtitle 관계 병합
        for subtitle in artist2.sub_titles.all():
            artist1.sub_titles.add(subtitle)

        # Article 관계 업데이트
        for article in artist2.article.all():
            article.artist.remove(artist2)
            article.artist.add(artist1)

        # Community 관계 업데이트
        for community in artist2.community.all():
            community.artist.remove(artist2)
            community.artist.add(artist1)

        # 3. Person 관계 병합
        # artist1의 person 필드에 artist2의 person 필드 추가
        for person in artist2.person.all():
            artist1.person.add(person)

        # 4. 병합 완료 후 artist2 삭제
        artist2.delete()

admin.site.register(Artist, ArtistAdmin)