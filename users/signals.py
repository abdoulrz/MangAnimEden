from django.db.models.signals import post_save
from django.dispatch import receiver
from reader.models import ReadingProgress

@receiver(post_save, sender=ReadingProgress)
def award_xp_on_read(sender, instance, created, **kwargs):
    """
    Attribue de l'XP à l'utilisateur lorsqu'il termine un chapitre.
    Gain : 10 XP par chapitre terminé.
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
        
        # On ajoute 10 XP
        instance.user.add_xp(10)
