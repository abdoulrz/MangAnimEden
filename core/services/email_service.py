from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """
        Envoie un email de bienvenue à l'utilisateur nouvellement inscrit.
        """
        subject = "Bienvenue sur MangaAnimEden !"
        # On pourrait utiliser un template HTML ici
        html_message = render_to_string('emails/welcome_email.html', {'user': user})
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@manganimeden.com',
                [user.email],
                html_message=html_message,
                fail_silently=True,  # Don't crash on email failure
            )
            return True
        except Exception as e:
            # Log error normally
            print(f"Error sending welcome email: {e}")
            return False

    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Envoie un email de réinitialisation de mot de passe.
        """
        pass # To be implemented with Django's built-in views or custom logic
