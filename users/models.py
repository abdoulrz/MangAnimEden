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
    
    # Gamification
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=100)

    # Online Status & Preferences (Phase 1 Expansion)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_dnd_mode = models.BooleanField(default=False, verbose_name="Mode Ne Pas Déranger")
    
    # Notification Preferences
    pref_notif_likes = models.BooleanField(default=True, verbose_name="Notifs J'aime")
    pref_notif_replies = models.BooleanField(default=True, verbose_name="Notifs Réponses")
    pref_notif_friends = models.BooleanField(default=True, verbose_name="Notifs Amis")
    pref_notif_messages = models.BooleanField(default=True, verbose_name="Notifs Messages")

    # Subscription & Access (New)
    has_nsfw_access = models.BooleanField(default=False, verbose_name="Accès 18+")
    SUBSCRIPTION_CHOICES = [
        ('free', 'Membre Gratuit'),
        ('premium', 'Abonné Premium'),
        ('legend', 'Membre Légende'),
    ]
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)

    # Rank System Metadata (Phase 4 Roadmap)
    RANK_DATA = {
        1:  {'title': 'Citoyen', 'slug': 'civilian', 'emoji': '🏘️', 'min_level': 1, 'color': '#95a5a6'},
        2:  {'title': 'Pirate Novice', 'slug': 'rookie-pirate', 'emoji': '🏴‍☠️', 'min_level': 5, 'color': '#7f8c8d'},
        3:  {'title': 'Exorciste Grade 4', 'slug': 'grade-4-sorcerer', 'emoji': '🧿', 'min_level': 10, 'color': '#3498db'},
        4:  {'title': 'Chasseur Rang-E', 'slug': 'e-rank-hunter', 'emoji': '🏹', 'min_level': 15, 'color': '#2980b9'},
        5:  {'title': 'Supernova', 'slug': 'supernova', 'emoji': '🌟', 'min_level': 20, 'color': '#f1c40f'},
        6:  {'title': 'Exorciste Grade 3', 'slug': 'grade-3-sorcerer', 'emoji': '🧿', 'min_level': 25, 'color': '#2ecc71'},
        7:  {'title': 'Chasseur Rang-C', 'slug': 'c-rank-hunter', 'emoji': '⚔️', 'min_level': 30, 'color': '#27ae60'},
        8:  {'title': 'Grand Corsaire', 'slug': 'warlord', 'emoji': '🔱', 'min_level': 40, 'color': '#e67e22'},
        9:  {'title': 'Exorciste Grade 1', 'slug': 'grade-1-sorcerer', 'emoji': '🧿', 'min_level': 45, 'color': '#d35400'},
        10: {'title': 'Chasseur Rang-S', 'slug': 's-rank-hunter', 'emoji': '🗡️', 'min_level': 50, 'color': '#e74c3c'},
        11: {'title': 'Commandant d\'Empereur', 'slug': 'yonko-commander', 'emoji': '🎖️', 'min_level': 65, 'color': '#c0392b'},
        12: {'title': 'Classe Spéciale', 'slug': 'special-grade', 'emoji': '🧿', 'min_level': 80, 'color': '#8e44ad'},
        13: {'title': 'Monarque des Ombres', 'slug': 'shadow-monarch', 'emoji': '👑', 'min_level': 100, 'color': '#2c3e50'},
    }

    def get_rank_info(self):
        """
        Retourne les informations du rang actuel basées sur le niveau.
        """
        current_rank = self.RANK_DATA[1]
        for rank_id, data in sorted(self.RANK_DATA.items()):
            if self.level >= data['min_level']:
                current_rank = data
            else:
                break
        return current_rank

    @property
    def is_online(self):
        """
        Vérifie si l'utilisateur est en ligne (vu il y a moins de 5 minutes).
        Masqué si le mode DND est activé.
        """
        if self.is_dnd_mode or not self.last_seen:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return self.last_seen > timezone.now() - timedelta(minutes=5)

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
        Utilise select_for_update() pour éviter les conflits de concurrence.
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Lock the user row for the duration of the transaction
            user = User.objects.select_for_update().get(pk=self.pk)
            user.xp += amount
            new_level = user.calculate_level()
            
            if new_level > user.level:
                user.level = new_level
                # Ici on pourrait ajouter une notification de "Level Up"
                
            user.save()
            
            # Update local instance to reflect DB changes
            self.xp = user.xp
            self.level = user.level

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

    def get_rank_display_name(self):
        """
        Returns the unified rank display name with its emoji.
        Replaces old Admin/Mod/Member labels site-wide.
        """
        rank = self.get_rank_info()
        return f"{rank['emoji']} {rank['title']}"

    @property
    def is_profile_complete(self):
        """
        Vérifie si le profil est considéré comme complet.
        Critères : Avatar, Bio, Pays et Ville sont remplis.
        """
        return bool(self.avatar and self.bio and self.location_country and self.location_city)

    # Hierarchy: Admin > Moderator > Reader > Banned
    role_admin = models.BooleanField(default=False, verbose_name="Administrateur")
    role_moderator = models.BooleanField(default=False, verbose_name="Modérateur")
    role_reader = models.BooleanField(default=True, verbose_name="Lecteur")

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
    
    def get_access_packs(self):
        """
        Retourne une liste des 'packs' ou contenus auxquels l'utilisateur a accès.
        Basé sur l'abonnement, le rang, et les flags d'accès.
        Max 5 items.
        """
        packs = []
        
        # 1. Type d'Abonnement (Inclus par défaut)
        packs.append({'name': self.get_subscription_type_display(), 'icon': '📜', 'type': 'membership'})
        
        # 2. Accès Adultes (Contenu 18+)
        if self.has_nsfw_access:
            packs.append({'name': 'Accès 18+', 'icon': '🔞', 'type': 'access'})
        
        # 3. Early Access (Basé sur le rang/niveau - voir ROADMAP Phase 4)
        rank = self.get_rank_info()
        if rank['min_level'] >= 20: # Supernova +
            days = 1
            if rank['min_level'] >= 40: days = 2
            if rank['min_level'] >= 65: days = 3
            packs.append({'name': f'Early Access (+{days}j)', 'icon': '⚡', 'type': 'perk'})
            
        # 4. Pack AnimWorld (Sera lié au système d'achat futur)
        # Pour l'instant, on simule l'accès pour les membres Légende ou haut niveau
        if self.subscription_type == 'legend' or self.level >= 30:
            packs.append({'name': 'AnimWorld VOD', 'icon': '🎬', 'type': 'content'})
            
        # 5. Pack Soutien (Placeholder pour "Contenu acheté")
        if self.subscription_type != 'free':
            packs.append({'name': 'Pack Pionnier', 'icon': '💎', 'type': 'bought'})
            
        return packs[:5]

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

