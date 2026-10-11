"""Services for core app."""
import logging
from .models import AuditLog


logger = logging.getLogger(__name__)


class AuditLogService:
    """Service for creating audit log entries."""
    
    @classmethod
    def log_action(cls, actor, action, target_model, target_id, details=None, ip_address=None):
        """
        Create an audit log entry.
        
        Args:
            actor: User who performed the action
            action: Action name (e.g., 'USER_DEACTIVATED', 'COMPANY_APPROVED')
            target_model: Model name (e.g., 'User', 'Company')
            target_id: ID of the target object
            details: Optional dict with additional details
            ip_address: Optional IP address
        
        Returns:
            AuditLog instance or None if failed
        """
        try:
            audit_log = AuditLog.objects.create(
                actor=actor,
                action=action,
                target_model=target_model,
                target_id=target_id,
                details=details or {},
                ip_address=ip_address
            )
            logger.info(f'Audit log created: {action} on {target_model}#{target_id} by {actor}')
            return audit_log
        except Exception as e:
            logger.error(f'Failed to create audit log: {e}')
            return None
