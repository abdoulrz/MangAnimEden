from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Badge, UserBadge


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ... existing code ...
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


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition_type', 'threshold')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'obtained_at')
    list_filter = ('badge__condition_type',)
    search_fields = ('user__nickname', 'badge__name')
