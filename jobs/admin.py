from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Skill, Job, JobReport
import logging

logger = logging.getLogger(__name__)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    
    list_display = ['name', 'slug', 'job_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def job_count(self, obj):
        """Display number of jobs in this category."""
        return obj.jobs.count()
    job_count.short_description = 'Number of Jobs'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin interface for Skill model."""
    
    list_display = ['name', 'job_count']
    search_fields = ['name']
    
    def job_count(self, obj):
        """Display number of jobs requiring this skill."""
        return obj.jobs.count()
    job_count.short_description = 'Number of Jobs'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for Job model."""
    
    list_display = ['title', 'company', 'category', 'job_type', 'location', 'active_badge', 'approval_badge', 'posted_at']
    list_filter = ['category', 'job_type', 'is_active', 'is_approved', 'posted_at']
    search_fields = ['title', 'company__name', 'location', 'description']
    readonly_fields = ['slug', 'posted_at', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['skills']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('company', 'title', 'slug', 'description', 'category', 'skills')
        }),
        ('Job Details', {
            'fields': ('location', 'job_type', 'salary_min', 'salary_max', 'deadline', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('posted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_jobs', 'reject_jobs', 'activate_jobs', 'deactivate_jobs']
    
    def active_badge(self, obj):
        """Display active status as badge."""
        color = 'success' if obj.is_active else 'secondary'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            text
        )
    active_badge.short_description = 'Active'
    
    def approval_badge(self, obj):
        """Display approval status as badge."""
        color = 'success' if obj.is_approved else 'warning'
        text = 'Approved' if obj.is_approved else 'Pending'
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            text
        )
    approval_badge.short_description = 'Approval'
    
    def approve_jobs(self, request, queryset):
        """Approve selected jobs."""
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} jobs have been approved.')
        logger.info(f'Admin {request.user.email} approved {count} jobs')
    approve_jobs.short_description = 'Approve selected jobs'
    
    def reject_jobs(self, request, queryset):
        """Reject (unapprove) selected jobs."""
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} jobs have been rejected.')
        logger.info(f'Admin {request.user.email} rejected {count} jobs')
    reject_jobs.short_description = 'Reject selected jobs'
    
    def activate_jobs(self, request, queryset):
        """Activate selected jobs."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} jobs have been activated.')
        logger.info(f'Admin {request.user.email} activated {count} jobs')
    activate_jobs.short_description = 'Activate selected jobs'
    
    def deactivate_jobs(self, request, queryset):
        """Deactivate selected jobs."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} jobs have been deactivated.')
        logger.info(f'Admin {request.user.email} deactivated {count} jobs')
    deactivate_jobs.short_description = 'Deactivate selected jobs'


@admin.register(JobReport)
class JobReportAdmin(admin.ModelAdmin):
    """Admin interface for JobReport model."""
    
    list_display = ['job', 'reporter', 'reason', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['job__title', 'reporter__email', 'description']
    readonly_fields = ['created_at', 'reviewed_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('job', 'reporter', 'reason', 'description')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
