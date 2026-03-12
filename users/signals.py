from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from reader.models import ReadingProgress

from .services import BadgeService

from core.services.email_service import EmailService

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    """
    Envoie un email de bienvenue à l'utilisateur lors de sa création.
    Phase 3.2 - Email System
    """
    if created and instance.email:
        EmailService.send_welcome_email(instance)

@receiver(pre_save, sender=ReadingProgress)
def track_completion_change(sender, instance, **kwargs):
    """Detects if the completed status is changing to True."""
    if not instance.pk:
        instance._was_completed = False
        return

    try:
        # Avoid direct QuerySet to keep it efficient
        old_obj = ReadingProgress.objects.only('completed').get(pk=instance.pk)
        instance._was_completed = old_obj.completed
    except ReadingProgress.DoesNotExist:
        instance._was_completed = False

@receiver(post_save, sender=ReadingProgress)
def award_xp_on_read(sender, instance, created, **kwargs):
    """
    Attribue de l'XP à l'utilisateur lorsqu'il termine un chapitre.
    Gain : 5 XP par chapitre terminé (attribué une seule fois).
    """
    was_completed = getattr(instance, '_was_completed', False)
    
    # On n'attribue l'XP que si 'completed' est True ET qu'il ne l'était pas avant
    if instance.completed and (created or not was_completed):
        instance.user.add_xp(5)
        BadgeService.check_badges(instance.user, 'CHAPTERS_READ')


@receiver(post_save, sender=User)
def check_and_promote_user(sender, instance, created, **kwargs):
    """
    Vérifie et met à jour automatiquement les rôles de l'utilisateur
    en fonction de son niveau.
    
    Phase 2.5.1 : Promotion automatique au rôle de modérateur à niveau 50.
    """
    # Éviter la récursion infinie : ne pas re-sauvegarder si on est
    # déjà dans un signal post_save
    if kwargs.get('update_fields') is not None:
        return
    
    # Vérifier et mettre à jour les rôles basés sur le niveau
    role_updated = instance.update_role_based_on_level()
    
    # Si le rôle a été mis à jour, sauvegarder les changements
    if role_updated:
        # Utiliser update_fields pour éviter de déclencher à nouveau tous les signaux
        instance.save(update_fields=['role_moderator'])
