from django.contrib import admin
from .models import Application, ApplicationStatusHistory


class ApplicationStatusHistoryInline(admin.TabularInline):
    """Inline admin for application status history."""
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'changed_at', 'note']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application model."""
    
    list_display = ['id', 'applicant', 'job', 'status', 'applied_at', 'updated_at']
    list_filter = ['status', 'applied_at', 'job__company']
    search_fields = ['applicant__email', 'applicant__first_name', 'applicant__last_name', 
                     'job__title', 'job__company__name']
    readonly_fields = ['applied_at', 'updated_at']
    date_hierarchy = 'applied_at'
    inlines = [ApplicationStatusHistoryInline]
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Content', {
            'fields': ('cover_letter',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    """Admin interface for ApplicationStatusHistory model."""
    
    list_display = ['id', 'application', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['new_status', 'changed_at']
    search_fields = ['application__applicant__email', 'application__job__title', 'note']
    readonly_fields = ['application', 'old_status', 'new_status', 'changed_by', 'changed_at', 'note']
    date_hierarchy = 'changed_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
