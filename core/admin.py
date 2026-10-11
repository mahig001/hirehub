from django.contrib import admin
from .models import ContactMessage, AuditLog


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin interface for ContactMessage model."""
    
    list_display = ['subject', 'name', 'email', 'is_read', 'created_at', 'responded_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    
    list_display = ['action', 'actor', 'target_model', 'target_id', 'created_at']
    list_filter = ['action', 'target_model', 'created_at']
    search_fields = ['action', 'actor__email', 'target_model']
    readonly_fields = ['actor', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'created_at']
    
    fieldsets = (
        ('Action', {
            'fields': ('actor', 'action', 'ip_address')
        }),
        ('Target', {
            'fields': ('target_model', 'target_id', 'details')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation of audit logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deletion of audit logs."""
        return False
