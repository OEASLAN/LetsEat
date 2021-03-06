from django.contrib import admin

from .models import Event, User


class UserAdmin(admin.ModelAdmin):

    list_display = ('name', 'surname', 'email', 'username', 'facebook_id')

    fieldsets = [
        ('Personal Infromation',    {'fields': ['photo', 'name', 'surname', 'password', 'username', 'facebook_id']}),
        ('Contact Information',     {'fields': ['email']}),
        ('Admin Privilage',         {'fields': ['is_admin', 'is_active']}),
    ]


admin.site.register(User, UserAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time')


admin.site.register(Event, EventAdmin)