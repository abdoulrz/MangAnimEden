from django.utils import timezone
from django.core.cache import cache

class UserStatusMiddleware:
    """
    Middleware pour mettre à jour la date de dernière activité de l'utilisateur.
    Utilisé pour l'indicateur "En ligne".
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # On utilise le cache pour éviter d'écrire en DB à CHAQUE requête
            # On ne met à jour la DB que toutes les minutes
            cache_key = f"last_seen_{request.user.id}"
            last_update = cache.get(cache_key)
            
            if not last_update:
                request.user.last_seen = timezone.now()
                request.user.save(update_fields=['last_seen'])
                # Expire après 60 secondes
                cache.set(cache_key, True, 60)
            
        response = self.get_response(request)
        return response
