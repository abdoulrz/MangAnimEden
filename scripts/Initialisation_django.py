# Exemple concret de code suivant les principes établis :
# 1. Documentation claire (Docstrings)
# 2. Séparation des rôles (Managers)
# 3. Préparation pour la communauté (Champs personnalisés)

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Manager personnalisé pour utiliser l'email comme identifiant unique
    au lieu du username, pratique courante pour les web apps modernes.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé.
    Inclut des champs pour la gamification et la communauté (Avatar, Bio, Level).
    """
    username = None # On retire le username par défaut
    email = models.EmailField(_('adresse email'), unique=True)
    
    # Profiling pour la communauté
    nickname = models.CharField(max_length=50, unique=True, verbose_name="Pseudo")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Gamification (Optionnel mais suggéré pour l'engagement communautaire)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = CustomUserManager()

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "Lecteur"
        verbose_name_plural = "Lecteurs"