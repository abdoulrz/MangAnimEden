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

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé.
    Inclut des champs pour la gamification et la communauté (Avatar, Bio, Level).
    """
    username = None  # On retire le username par défaut
    email = models.EmailField(_('adresse email'), unique=True)
    
    # Profiling pour la communauté
    nickname = models.CharField(max_length=50, unique=True, verbose_name="Pseudo")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Gamification (Optionnel mais suggéré pour l'engagement communautaire)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)

    def calculate_level(self):
        """
        Calcule le niveau basé sur l'XP total.
        Formule simple : Niveau = (XP // 100) + 1
        """
        return (self.xp // 100) + 1

    def add_xp(self, amount):
        """
        Ajoute de l'XP et met à jour le niveau si nécessaire.
        """
        self.xp += amount
        new_level = self.calculate_level()
        
        if new_level > self.level:
            self.level = new_level
            # Ici on pourrait ajouter une notification de "Level Up"
            
        self.save()

    def get_level_progress(self):
        """
        Retourne le pourcentage de progression vers le prochain niveau
        et les valeurs XP actuelles/requises.
        """
        xp_per_level = 100
        current_level_xp_start = (self.level - 1) * xp_per_level
        next_level_xp_target = self.level * xp_per_level
        
        xp_in_current_level = self.xp - current_level_xp_start
        progress_percent = (xp_in_current_level / xp_per_level) * 100
        
        return {
            'current': self.xp,
            'next': next_level_xp_target,
            'percent': min(max(progress_percent, 0), 100)  # Clamp between 0-100
        }

    # Roles (Activités)
    role_admin = models.BooleanField(default=False, verbose_name="Administrateur")
    role_moderator = models.BooleanField(default=False, verbose_name="Modérateur")
    role_reader = models.BooleanField(default=True, verbose_name="Lecteur")
    role_translator = models.BooleanField(default=False, verbose_name="Traducteur")
    role_editor = models.BooleanField(default=False, verbose_name="Éditeur")
    role_author = models.BooleanField(default=False, verbose_name="Auteur")

    # Status
    is_banned = models.BooleanField(default=False, verbose_name="Banni")

    # Réseaux Sociaux
    social_facebook = models.URLField(blank=True, verbose_name="Facebook")
    social_twitter = models.URLField(blank=True, verbose_name="Twitter / X")
    social_instagram = models.URLField(blank=True, verbose_name="Instagram")
    social_youtube = models.URLField(blank=True, verbose_name="YouTube")
    social_linkedin = models.URLField(blank=True, verbose_name="LinkedIn")

    # Localisation
    location_country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    location_city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = CustomUserManager()

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "Lecteur"
        verbose_name_plural = "Lecteurs"
