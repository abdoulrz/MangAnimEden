import logging
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@shared_task
def task_send_welcome_email(user_id):
    """
    Tâche asynchrone pour envoyer l'email de bienvenue.
    """
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        subject = "Bienvenue sur MangAnimEDen !"
        
        # Contexte pour le template
        context = {
            'user': user,
            'site_name': 'MangAnimEDen',
            'site_domain': getattr(settings, 'SITE_URL', 'https://manganimeden.net')
        }
        
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@manganimeden.net'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email successfully sent to {user.email}")
        return True
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send welcome email to User ID {user_id}: {e}")
        return False

@shared_task
def task_send_password_reset_email(user_id, reset_url):
    """
    Tâche asynchrone pour envoyer l'email de réinitialisation de mot de passe.
    """
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        subject = "Réinitialisation de votre mot de passe - MangAnimEDen"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'MangAnimEDen',
            'site_domain': getattr(settings, 'SITE_URL', 'https://manganimeden.net')
        }
        
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@manganimeden.net'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to User ID {user_id}: {e}")
        return False

@shared_task
def task_send_moderation_alert_email(user_id, reason, warning_level):
    """
    Tâche asynchrone pour avertissement de modération.
    """
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        subject = f"Avertissement de Modération (Niveau {warning_level}) - MangAnimEDen"
        
        context = {
            'user': user,
            'reason': reason,
            'warning_level': warning_level,
            'site_name': 'MangAnimEDen',
            'site_domain': getattr(settings, 'SITE_URL', 'https://manganimeden.net')
        }
        
        html_message = render_to_string('emails/moderation_alert.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@manganimeden.net'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send moderation email: {e}")
        return False
