from django.contrib import admin

from communityapp.models import Community
# Register your models here.
# admin.py

class CommunityAdmin(admin.ModelAdmin):
    
    actions = ['make_hidden', 'make_not_hidden']

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected communitys as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected communitys as not hidden"

admin.site.register(Community, CommunityAdmin)
