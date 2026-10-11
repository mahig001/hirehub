from .services import NotificationService
from .models import Notification


def notifications_context(request):
    """
    Context processor to add notification data to all templates.
    
    Returns unread notification count and recent notifications for authenticated users.
    """
    if not request.user.is_authenticated:
        return {
            'unread_notifications_count': 0,
            'recent_notifications': []
        }
    
    return {
        'unread_notifications_count': NotificationService.get_unread_count(request.user),
        'recent_notifications': Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
    }
