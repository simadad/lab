from django.contrib import admin
from .models import LabUser, Paper, UserInfoQ, UserInfoA, UserAttr, AttrOption
# Register your models here.


class AttrOptionInline(admin.TabularInline):
    model = AttrOption


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
    fieldsets = (
        ['Main', {
            'fields': ('user', 'nickname', 'wechat')
        }],
    )


class PaperAdmin(admin.ModelAdmin):
    inlines = [InfoQInline]
    list_filter = ('create_time', 'finished_time', 'is_del')
    list_display = ('user', 'create_time', 'finished_time', 'is_del')
    search_fields = ('user',)
    fieldsets = (
        ['Main', {
            'fields': ('user', 'finished_time', 'is_del')
        }],
    )


class UserAttrAdmin(admin.ModelAdmin):
    inlines = [InfoQInline, AttrOptionInline]
    list_display = ('attr', 'is_option')
    list_filter = ('attr', 'is_option')
    search_fields = ('attr',)
    fieldsets = (
        ['Main', {
            'fields': ('attr', 'is_option')
        }],
    )


class UserInfoQAdmin(admin.ModelAdmin):
    inlines = [InfoAInline]
    list_display = ('user', 'paper', 'attr', 'is_del')
    list_filter = ('paper', 'attr', 'is_del')
    search_fields = ('user', 'paper', 'attr')
    fieldsets = (
        ['Main', {
            'fields': ('user', 'paper', 'attr', 'is_del')
        }],
    )


class UserInfoAAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'create_time', 'is_del')
    list_filter = ('question', 'answer', 'is_del')
    search_fields = ('user', 'question', 'answer')
    fieldsets = (
        ['Main', {
            'fields': ('user', 'question', 'answer', 'is_del')
        }],
    )


class AttrOptionAdmin(admin.ModelAdmin):
    list_display = ('option', 'attr')
    list_filter = ('option', 'attr')
    search_fields = ('option', 'attr')
    fieldsets = (
        ['Main', {
            'fields': ('option', 'attr')
        }],
    )

admin.site.register(LabUser, LabUserAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(UserInfoQ, UserInfoQAdmin)
admin.site.register(UserInfoA, UserInfoAAdmin)
admin.site.register(UserAttr, UserAttrAdmin)
admin.site.register(AttrOption, AttrOptionAdmin)
