from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    readonly_fields = ['avatar']

    def avatar(self, obj):
        if obj:
            return mark_safe(
            '<img src="/static/{url}" width="120" />'\
            .format(url=obj.image.name)
    )


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'date_joined']
    readonly_fields = ['avatar_user']

    def avatar_user(self, obj):
        if obj:
            return mark_safe(
            '<img src="/static/{url}" width="120" />'\
            .format(url=obj.avatar.name)
    )

admin.site.register(Category)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(User, UserAdmin)
