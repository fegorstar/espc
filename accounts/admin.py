from django.contrib import admin
from .models import User
from django.utils.html import format_html


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email',
                    'user_type', 'is_active', 'last_login')
    list_display_links = ('id', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'created_at')
    ordering = ('-created_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    # when creating User(student,tutor.,admin) through Admin Panel - Getting Password Hatched
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        else:
            current_password = User.objects.get(pk=obj.pk).password
            if current_password != obj.password:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
