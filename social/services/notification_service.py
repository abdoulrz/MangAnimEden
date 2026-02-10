from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from social.models import Notification

class NotificationService:
    @staticmethod
    def create_notification(recipient, actor, verb, type, target=None):
        """
        Crée une notification de manière sécurisée.
        """
        if recipient == actor:
            return None  # Don't notify users of their own actions
            
        try:
            notification = Notification(
                recipient=recipient,
                actor=actor,
                verb=verb,
                notification_type=type,
            )
            
            if target:
                notification.content_type = ContentType.objects.get_for_model(target)
                notification.object_id = target.id
                
            notification.save()
            return notification
        except Exception as e:
            # Silent fail for notifications (non-critical)
            print(f"Error creating notification: {e}")
            return None

    @staticmethod
    def mark_as_read(user, notification_id=None):
        """
        Marque une ou toutes les notifications comme lues.
        """
        qs = Notification.objects.filter(recipient=user, is_read=False)
        
        if notification_id:
            qs = qs.filter(id=notification_id)
            
        updated_count = qs.update(is_read=True)
        return updated_count

    @staticmethod
    def get_unread_count(user):
        if not user.is_authenticated:
            return 0
        return Notification.objects.filter(recipient=user, is_read=False).count()
