from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Employee
import logging

logger = logging.getLogger(__name__)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model."""
    
    list_display = ['name', 'owner', 'industry', 'size', 'location', 'status_badge', 'created_at']
    list_filter = ['status', 'industry', 'size', 'created_at']
    search_fields = ['name', 'owner__email', 'owner__first_name', 'owner__last_name', 'location']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Company Information', {
            'fields': ('owner', 'name', 'slug', 'logo', 'website', 'industry', 'size', 'location', 'about')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_companies', 'reject_companies', 'suspend_companies']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'PENDING': 'warning',
            'VERIFIED': 'success',
            'REJECTED': 'danger',
            'SUSPENDED': 'secondary',
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_companies(self, request, queryset):
        """Approve selected companies."""
        count = queryset.update(status=Company.VERIFIED, rejection_reason='')
        self.message_user(request, f'{count} companies have been approved.')
        logger.info(f'Admin {request.user.email} approved {count} companies')
    approve_companies.short_description = 'Approve selected companies'
    
    def reject_companies(self, request, queryset):
        """Reject selected companies."""
        count = queryset.update(status=Company.REJECTED)
        self.message_user(request, f'{count} companies have been rejected.')
        logger.info(f'Admin {request.user.email} rejected {count} companies')
    reject_companies.short_description = 'Reject selected companies'
    
    def suspend_companies(self, request, queryset):
        """Suspend selected companies."""
        count = queryset.update(status=Company.SUSPENDED)
        self.message_user(request, f'{count} companies have been suspended.')
        logger.info(f'Admin {request.user.email} suspended {count} companies')
    suspend_companies.short_description = 'Suspend selected companies'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    
    list_display = ['user', 'company', 'position', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company__name', 'position']
    readonly_fields = ['created_at']
