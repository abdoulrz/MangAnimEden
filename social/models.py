from django.db import models
from django.conf import settings


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='group_icons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_groups', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.owner:
             # Basic validation, though better handled in forms/views for user feedback
             pass
        super().save(*args, **kwargs)


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        status = "Banned" if self.is_banned else "Member"
        return f"{self.user.nickname} in {self.group.name} ({status})"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name = "Événement"

    def __str__(self):
        return self.title

class Message(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # New Fields for Social Features (Phase 3.2)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_messages', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.sender} in {self.group}: {self.content[:20]}"
    
    @property
    def like_count(self):
        return self.likes.count()


class DirectMessage(models.Model):
    """
    Modèle pour les messages privés entre amis.
    Phase 1 Expansion - SPEC-012
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_dms', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_dms', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # DM Interactions (Reply + Like)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_dms', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='dm_replies', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'recipient', 'timestamp']),
        ]

    def __str__(self):
        return f"DM from {self.sender} to {self.recipient}"

    @property
    def like_count(self):
        return self.likes.count()


# ========== NOTIFICATIONS (Phase 3.2) ==========

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """
    Système de notification unifié.
    Types: System, Like, Reply, Friend Request.
    """
    TYPE_CHOICES = [
        ('system', 'Système'),
        ('like', 'J\'aime'),
        ('reply', 'Réponse'),
        ('friend_request', 'Demande d\'ami'),
        ('friend_accept', 'Ami accepté'),
        ('message', 'Message Privé'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='notifications', 
        on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='triggered_notifications', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    verb = models.CharField(max_length=255)  # e.g., "a aimé votre message", "vous a envoyé une demande"
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    
    # Generic Relation to target object (Message, User, Chapter, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]
        
    def __str__(self):
        actor_name = self.actor.nickname if self.actor else "System"
        return f"Notif for {self.recipient}: {actor_name} {self.verb}"

    def get_target_url(self):
        """
        Returns a deep-link URL so the user can jump directly to the source
        of this notification (DM conversation, group chat, or profile).
        """
        try:
            if self.notification_type == 'message' and self.actor:
                # DM notification → open the DM conversation with the sender
                return f'/forum/?dm_id={self.actor.id}'
            elif self.notification_type in ('like', 'reply') and self.target:
                # Group message interaction → open the group chat
                # target is a Message object; navigate to the group
                group_id = getattr(self.target, 'group_id', None)
                if group_id:
                    return f'/forum/?group_id={group_id}'
            elif self.notification_type in ('friend_request', 'friend_accept') and self.actor:
                # Open the actor's public profile
                return f'/users/user/{self.actor.id}/'
        except Exception:
            pass
        # Fallback: notifications list
        return '/social/notifications/'


from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_delete
import os

class Story(models.Model):
    """
    Modèle polymorphique pour les Stories de groupe.
    Supporte deux types de noeud : Media (image/vidéo) et Texte (fond coloré + texte).
    """
    NODE_TYPES = [
        ('media', 'Image/Video Media'),
        ('text', 'Rich Text Block'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stories', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='stories', on_delete=models.SET_NULL, null=True, blank=True)
    node_type = models.CharField(max_length=10, choices=NODE_TYPES, default='media')

    # Common Fields
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # For Media Stories (Images/Videos)
    image = models.ImageField(upload_to='stories/', null=True, blank=True)

    # For Text Stories
    text_content = models.TextField(null=True, blank=True)
    background_color = models.CharField(max_length=7, default='#6c5ce7')  # Hex code
    background_image = models.ImageField(upload_to='forum/stories/backgrounds/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Story ({self.get_node_type_display()}) by {self.user} ({self.created_at})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Story"


@receiver(post_delete, sender=Story)
def cleanup_story_file(sender, instance, **kwargs):
    """Supprime les fichiers physiques lors de la suppression de la Story."""
    for field in [instance.image, instance.background_image]:
        if field:
            try:
                if os.path.isfile(field.path):
                    os.remove(field.path)
            except Exception:
                pass  # Gracefully handle R2/cloud files that don't have a local path


class Friendship(models.Model):
    """
    Modèle pour gérer les relations d'amitié entre utilisateurs.
    Phase 2.5.2 - Système Social (Amis)
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
    ]
    
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='friendship_requests_sent',
        on_delete=models.CASCADE,
        verbose_name="Demandeur"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='friendship_requests_received',
        on_delete=models.CASCADE,
        verbose_name="Destinataire"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        unique_together = ('requester', 'receiver')
        ordering = ['-created_at']
        verbose_name = "Amitié"
        verbose_name_plural = "Amitiés"
    
    def __str__(self):
        return f"{self.requester.nickname} -> {self.receiver.nickname} ({self.status})"
    
    def accept(self):
        """Accepter la demande d'amitié"""
        self.status = 'accepted'
        self.save()
    
    def is_pending(self):
        """Vérifier si la demande est en attente"""
        return self.status == 'pending'
    
    def is_accepted(self):
        """Vérifier si la demande est acceptée"""
        return self.status == 'accepted'
