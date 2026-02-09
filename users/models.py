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
    xp = models.PositiveIntegerField(default=100)

    def calculate_level(self):
        """
        Calcule le niveau basé sur l'XP total.
        Formule simple : Niveau = XP // 100
        (100 XP = Niveau 1, 5000 XP = Niveau 50)
        """
        return self.xp // 100

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
        # Use calculated level to ensure targets are correct even if DB level is stale
        current_calculated_level = self.calculate_level()
        xp_per_level = 100
        current_level_xp_start = current_calculated_level * xp_per_level
        next_level_xp_target = (current_calculated_level + 1) * xp_per_level
        
        xp_in_current_level = self.xp - current_level_xp_start
        progress_percent = (xp_in_current_level / xp_per_level) * 100
        
        return {
            'current': self.xp,
            'next': next_level_xp_target,
            'percent': min(max(progress_percent, 0), 100)  # Clamp between 0-100
        }

    def update_role_based_on_level(self):
        """
        Met à jour automatiquement les rôles de l'utilisateur en fonction de son niveau.
        À niveau 50 (500 chapitres lus) : promotion automatique au rôle de modérateur.
        
        Returns:
            bool: True si le rôle a été mis à jour, False sinon.
        """
        role_updated = False
        
        # Promotion automatique au rôle de modérateur à niveau 50
        if self.level >= 50 and not self.role_moderator:
            self.role_moderator = True
            role_updated = True
        
        return role_updated

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

    # Friend Management Methods (Phase 2.5.2)
    def get_friends(self):
        """
        Retourne tous les amis acceptés de l'utilisateur.
        """
        from social.models import Friendship
        from django.db.models import Q
        
        # Friends where this user is the requester
        friends_as_requester = User.objects.filter(
            friendship_requests_received__requester=self,
            friendship_requests_received__status='accepted'
        )
        # Friends where this user is the receiver
        friends_as_receiver = User.objects.filter(
            friendship_requests_sent__receiver=self,
            friendship_requests_sent__status='accepted'
        )
        return (friends_as_requester | friends_as_receiver).distinct()

    def get_friend_count(self):
        """
        Retourne le nombre d'amis acceptés.
        """
        return self.get_friends().count()

    def get_pending_requests(self):
        """
        Retourne les demandes d'amitié en attente reçues par cet utilisateur.
        """
        from social.models import Friendship
        return Friendship.objects.filter(receiver=self, status='pending')
    
    def get_pending_requests_count(self):
        """
        Retourne le nombre de demandes d'amitié en attente.
        """
        return self.get_pending_requests().count()

    def is_friend_with(self, other_user):
        """
        Vérifie si deux utilisateurs sont amis.
        """
        from social.models import Friendship
        from django.db.models import Q
        
        return Friendship.objects.filter(
            Q(requester=self, receiver=other_user, status='accepted') |
            Q(requester=other_user, receiver=self, status='accepted')
        ).exists()
    
    def has_pending_request_from(self, other_user):
        """
        Vérifie si cet utilisateur a une demande en attente de other_user.
        """
        from social.models import Friendship
        return Friendship.objects.filter(
            requester=other_user,
            receiver=self,
            status='pending'
        ).exists()
    
    def has_sent_request_to(self, other_user):
        """
        Vérifie si cet utilisateur a envoyé une demande à other_user.
        """
        from social.models import Friendship
        return Friendship.objects.filter(
            requester=self,
            receiver=other_user,
            status='pending'
        ).exists()

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "Lecteur"
        verbose_name_plural = "Lecteurs"


class Badge(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    
    CONDITION_CHOICES = [
        ('CHAPTERS_READ', 'Chapitres Lus'),
        ('SERIES_COMPLETED', 'Séries Terminées'),
        ('COMMENTS_POSTED', 'Commentaires Postés'),
        ('ACCOUNT_AGE', 'Ancienneté (Jours)'),
        ('GROUP_JOINED', 'Groupes Rejoints'),
    ]
    condition_type = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    threshold = models.PositiveIntegerField(help_text="Valeur cible pour débloquer (ex: 100 pour 100 chapitres)")
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')

