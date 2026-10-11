import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for handling notifications and emails."""
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, link=''):
        """
        Create a notification for a user.
        
        Args:
            recipient: User instance
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            link: Optional URL link
        
        Returns:
            Notification instance or None if error
        """
        try:
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link
            )
            logger.info(f'Created notification {notification.id} for user {recipient.id}')
            return notification
        except Exception as e:
            logger.error(f'Error creating notification: {e}')
            return None
    
    @classmethod
    def send_email_notification(cls, recipient, subject, template_name, context):
        """
        Send an email notification to a user.
        
        Args:
            recipient: User instance or email address
            subject: Email subject
            template_name: Template path (e.g., 'notifications/emails/template.html')
            context: Dictionary of context variables for the template
        
        Returns:
            Boolean indicating success
        """
        try:
            # Get recipient email
            recipient_email = recipient.email if hasattr(recipient, 'email') else recipient
            
            # Render email template
            html_message = render_to_string(template_name, context)
            
            # Send email
            send_mail(
                subject=subject,
                message='',  # Plain text version (empty for now)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            logger.info(f'Sent email to {recipient_email} with subject: {subject}')
            return True
        except Exception as e:
            logger.error(f'Error sending email: {e}')
            return False
    
    @classmethod
    def mark_as_read(cls, notification_id, user):
        """
        Mark a single notification as read.
        
        Args:
            notification_id: ID of the notification
            user: User instance (for ownership verification)
        
        Returns:
            Boolean indicating success
        """
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.is_read = True
            notification.save()
            logger.info(f'Marked notification {notification_id} as read for user {user.id}')
            return True
        except Notification.DoesNotExist:
            logger.warning(f'Notification {notification_id} not found for user {user.id}')
            return False
        except Exception as e:
            logger.error(f'Error marking notification as read: {e}')
            return False
    
    @classmethod
    def mark_all_as_read(cls, user):
        """
        Mark all unread notifications as read for a user.
        
        Args:
            user: User instance
        
        Returns:
            Integer count of notifications marked as read
        """
        try:
            count = Notification.objects.filter(
                recipient=user,
                is_read=False
            ).update(is_read=True)
            logger.info(f'Marked {count} notifications as read for user {user.id}')
            return count
        except Exception as e:
            logger.error(f'Error marking all notifications as read: {e}')
            return 0
    
    @classmethod
    def get_unread_count(cls, user):
        """
        Get the count of unread notifications for a user.
        
        Args:
            user: User instance
        
        Returns:
            Integer count of unread notifications
        """
        try:
            count = Notification.objects.filter(
                recipient=user,
                is_read=False
            ).count()
            return count
        except Exception as e:
            logger.error(f'Error getting unread count: {e}')
            return 0
