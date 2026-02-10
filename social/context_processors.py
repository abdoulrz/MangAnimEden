from social.models import Notification

def notifications(request):
    """
    Injecte les notifications non lues et récentes dans le contexte global.
    Utilisé pour la navbar.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        latest_notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('actor', 'content_type').order_by('-created_at')[:5]
        
        return {
            'notification_count': unread_count,
            'navbar_notifications': latest_notifications
        }
    return {
        'notification_count': 0,
        'navbar_notifications': []
    }
