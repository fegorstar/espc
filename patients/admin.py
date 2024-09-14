from django.contrib import admin
from .models import Profile
from django.utils.html import format_html


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'state', 'city', 'phone_number', 'nin', 'created_at', 'updated_at')
    list_display_links = ('user_email',)
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'


admin.site.register(Profile, ProfileAdmin)
