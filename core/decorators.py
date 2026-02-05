from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def requires_role(role_name):
    """
    Decorator for views that checks if the user has a specific role.
    Usage: @requires_role('moderator')
    checks for user.role_moderator == True
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
        def _wrapped_view(request, *args, **kwargs):
            if not check_role(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def requires_admin(view_func):
    """
    Shortcut for @requires_role('admin')
    """
    return requires_role('admin')(view_func)

def requires_moderator(view_func):
    """
    Shortcut for @requires_role('moderator')
    """
    return requires_role('moderator')(view_func)
