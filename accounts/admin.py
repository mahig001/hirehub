from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, JobSeekerProfile, Education, Experience


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


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for JobSeekerProfile model."""
    
    list_display = ['user', 'headline', 'location', 'completeness', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'headline', 'location']
    raw_id_fields = ['user']
    filter_horizontal = ['saved_jobs']
    readonly_fields = ['created_at', 'updated_at', 'completeness']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Profile Information'), {
            'fields': ('headline', 'bio', 'location', 'phone', 'avatar', 'resume')
        }),
        (_('Saved Jobs'), {'fields': ('saved_jobs',)}),
        (_('Metadata'), {'fields': ('completeness', 'created_at', 'updated_at')}),
    )
    
    def completeness(self, obj):
        """Display profile completeness percentage."""
        return f"{obj.calculate_completeness()}%"
    completeness.short_description = "Completeness"


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin configuration for Education model."""
    
    list_display = ['user', 'degree', 'field_of_study', 'institution', 'start_date', 'end_date']
    list_filter = ['degree', 'start_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 
                     'degree', 'field_of_study', 'institution']
    raw_id_fields = ['user']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Education Details'), {
            'fields': ('degree', 'field_of_study', 'institution', 
                      'start_date', 'end_date', 'description')
        }),
        (_('Metadata'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin configuration for Experience model."""
    
    list_display = ['user', 'title', 'company_name', 'location', 'start_date', 
                    'end_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 
                     'title', 'company_name', 'location']
    raw_id_fields = ['user']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Experience Details'), {
            'fields': ('title', 'company_name', 'location', 
                      'start_date', 'end_date', 'is_current', 'description')
        }),
        (_('Metadata'), {'fields': ('created_at', 'updated_at')}),
    )
