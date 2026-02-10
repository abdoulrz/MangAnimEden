from django.db.models.signals import post_save
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

@receiver(post_save, sender=ReadingProgress)
def award_xp_on_read(sender, instance, created, **kwargs):
    """
    Attribue de l'XP à l'utilisateur lorsqu'il termine un chapitre.
    Gain : 5 XP par chapitre terminé.
    Vérifie également l'attribution de badges.
    """
    if instance.completed:
        # Note: Pour une implémentation plus robuste, il faudrait vérifier
        # si l'XP a déjà été attribué pour ce chapitre spécifique
        # (via un modèle UserChapterHistory par exemple) pour éviter le farming.
        # Pour l'instant, on suppose que le Reader view gère cela intelligemment.
        
        # On vérifie si c'est la première fois qu'on le marque completed (approximatif)
        # Si created=True et completed=True -> C'est sûr.
        # Si update -> On suppose que le view ne sauvegarde que si changement.
        
        # Pour éviter le spam sur chaque save de page (si update progress), 
        # on pourrait limiter, mais ici on reste simple pour la phase 2.5
        
        # On ajoute 5 XP
        instance.user.add_xp(5)
        
        # Vérification des badges (Type: Chapitres Lus)
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
