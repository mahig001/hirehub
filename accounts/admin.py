from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 
                    'is_email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'is_email_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 
                      'is_email_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 
                      'password1', 'password2', 'is_email_verified'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    actions = ['activate_users', 'deactivate_users', 'verify_emails']
    
    def activate_users(self, request, queryset):
        """Activate selected users."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) successfully activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def verify_emails(self, request, queryset):
        """Verify emails for selected users."""
        count = queryset.update(is_email_verified=True)
        self.message_user(request, f'{count} email(s) successfully verified.')
    verify_emails.short_description = "Verify emails for selected users"
