from django.conf import settings

def static_version(request):
    """
    Context processor that adds STATIC_VERSION to the context.
    """
    return {
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0.0')
    }
