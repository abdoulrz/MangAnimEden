from django.utils import timezone
from .models import Badge, UserBadge
from reader.models import ReadingProgress

class BadgeService:
    @staticmethod
    def check_badges(user, condition_type):
        """
        Vérifie et attribue les badges pour un type de condition donné.
        Retourne la liste des badges nouvellement acquis.
        """
        # Badges potentiels de ce type
        potential_badges = Badge.objects.filter(condition_type=condition_type)
        
        # Badges déjà acquis
        existing_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        
        newly_awarded = []
        
        for badge in potential_badges:
            if badge.id in existing_badge_ids:
                continue
                
            awarded = False
            
            if condition_type == 'CHAPTERS_READ':
                # Compter les chapitres lus
                count = ReadingProgress.objects.filter(user=user, completed=True).count()
                if count >= badge.threshold:
                    awarded = True
                    
            elif condition_type == 'ACCOUNT_AGE':
                delta = timezone.now() - user.date_joined
                if delta.days >= badge.threshold:
                    awarded = True
            
            # TODO: Implémenter les autres types de conditions au besoin
            
            if awarded:
                UserBadge.objects.create(user=user, badge=badge)
                newly_awarded.append(badge)
                
        return newly_awarded
