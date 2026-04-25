import logging
from core.tasks import task_send_welcome_email, task_send_password_reset_email, task_send_moderation_alert_email

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """
        Envoie un email de bienvenue à l'utilisateur de manière asynchrone via Celery.
        """
        try:
            # On passe l'ID et non l'objet User complet car Celery a besoin de sérialiser les données (JSON)
            task_send_welcome_email.delay(user.id)
            return True
        except Exception as e:
            logger.error(f"Failed to queue welcome email task for user {user.id}: {e}")
            return False

    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Envoie un email de réinitialisation de mot de passe de manière asynchrone.
        """
        try:
            task_send_password_reset_email.delay(user.id, reset_url)
            return True
        except Exception as e:
            logger.error(f"Failed to queue password reset email task for user {user.id}: {e}")
            return False

    @staticmethod
    def send_moderation_alert(user, reason, warning_level=1):
        """
        Envoie un email d'avertissement de modération de manière asynchrone.
        """
        try:
            task_send_moderation_alert_email.delay(user.id, reason, warning_level)
            return True
        except Exception as e:
            logger.error(f"Failed to queue moderation alert email for user {user.id}: {e}")
            return False
