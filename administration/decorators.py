from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from functools import wraps
from .models import SystemLog

def requires_role(role_name):
    """
    Décorateur qui vérifie si l'utilisateur a un rôle spécifique.
    Si l'utilisateur n'est pas connecté ou n'a pas le rôle, lève une Http404
    pour masquer l'existence de la page.
    """
    def check_role(user):
        if not user.is_authenticated:
            return False
        
        # Superuser always passes
        if user.is_superuser:
            return True
            
        # Check for specific role flag
        role_field = f'role_{role_name}'
        if hasattr(user, role_field):
            return getattr(user, role_field)
            
        return False

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not check_role(request.user):
                raise Http404("Page not found")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def requires_admin(view_func):
    return requires_role('admin')(view_func)

def requires_moderator(view_func):
    return requires_role('moderator')(view_func)

def create_system_log(request, action_type, target_user=None, details=None):
    """
    Helper function to create a system log entry.
    """
    try:
        ip = request.META.get('REMOTE_ADDR')
        
        # If no explicit details provided, try to capture from request
        if not details and request.method == 'POST':
             # Filter sensitive data if needed, for now just a simple dict
             details = f"Path: {request.path}"
        
        SystemLog.objects.create(
            actor=request.user,
            action=action_type,
            target_user=target_user,
            details=details,
            ip_address=ip
        )
    except Exception as e:
        print(f"Failed to create system log: {e}")

def log_admin_action(action_type):
    """
    Decorator for views (functions) that take 'request' as the first argument.
    Use this on view methods like 'post' or functions.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            if request.method == 'POST':
                 # Try to find target user if present in POST data for generic logging or use generic logic
                 target_user = None
                 target_user_id = request.POST.get('user_id') or request.POST.get('target_user_id')
                 
                 if target_user_id:
                     from django.contrib.auth import get_user_model
                     User = get_user_model()
                     try:
                         target_user = User.objects.get(pk=target_user_id)
                     except User.DoesNotExist:
                         pass
                 
                 create_system_log(request, action_type, target_user=target_user)
            
            return response
        return _wrapped_view
    return decorator
