from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuration de l'interface admin pour le modèle User personnalisé.
    """
    list_display = ['email', 'nickname', 'level', 'xp', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'level']
    search_fields = ['email', 'nickname']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nickname', 'avatar', 'bio')}),
        ('Gamification', {'fields': ('level', 'xp')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2'),
        }),
    )
