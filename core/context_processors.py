from django.conf import settings

def firebase_config(request):
    """
    Injects Firebase configuration into the template context.
    """
    return {
        'FIREBASE_CONFIG': settings.FIREBASE_CONFIG
    }
