from django.contrib import admin
from .models import LabUser, Paper, UserInfoQ, UserInfoA, UserAttr
# Register your models here.


class InfoAInline(admin.TabularInline):
    model = UserInfoA


class InfoQInline(admin.TabularInline):
    model = UserInfoQ


class PaperInline(admin.TabularInline):
    model = Paper


class LabUserAdmin(admin.ModelAdmin):
    inlines = [InfoQInline, InfoAInline, PaperInline]
    list_display = ('user', 'nickname', 'wechat')
    search_fields = ('user', 'nickname', 'wechat')
    list_filter = ('user', 'nickname', 'wechat')
    fieldsets = (
        ['Main', {
            'fields': ('user', 'nickname', 'wechat')
        }],
    )


class PaperAdmin(admin.ModelAdmin):
    inlines = [InfoQInline]
    list_filter = ('user', 'create_time', 'finished_time')
    list_display = ('user', 'create_time', 'finished_time')
    search_fields = ('user',)
    fieldsets = (
        ['Main', {
            'fields': ('user', 'finished_time')
        }],
    )


class UserAttrAdmin(admin.ModelAdmin):
    inlines = [InfoQInline]
    list_display = ('attr', 'is_option', 'options')
    list_filter = ('attr', 'is_option', 'options')
    search_fields = ('attr', 'is_option', 'options')
    fieldsets = (
        ['Main', {
            'fields': ('attr', 'is_option', 'options')
        }],
    )


class UserInfoQAdmin(admin.ModelAdmin):
    inlines = [InfoAInline]
    list_display = ('user', 'paper', 'attr')
    list_filter = ('user', 'paper', 'attr')
    search_fields = ('user', 'paper', 'attr')
    fieldsets = (
        ['Main', {
            'fields': ('user', 'paper', 'attr')
        }],
    )


class UserInfoAAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'create_time', 'modify_time')
    list_filter = ('user', 'question', 'answer')
    search_fields = ('user', 'question', 'answer')
    fieldsets = (
        ['Main', {
            'fields': ('user', 'question', 'answer')
        }],
    )

admin.site.register(LabUser, LabUserAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(UserInfoQ, UserInfoQAdmin)
admin.site.register(UserInfoA, UserInfoAAdmin)
admin.site.register(UserAttr, UserAttrAdmin)
