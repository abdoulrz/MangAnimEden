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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name = "Événement"

    def __str__(self):
        return self.title

class Message(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.sender} in {self.group}: {self.content[:20]}"


from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_delete
import os

class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stories', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stories/')
    created_at = models.DateTimeField(auto_now_add=True)
    # expires_at could be a field if we want custom expiration, but 24h rule is standard
    # We can calculate it on the fly or store it. Let's store it for index performance on cleanup
    expires_at = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey(Group, related_name='stories', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Story by {self.user} ({self.created_at})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Story"


@receiver(post_delete, sender=Story)
def cleanup_story_file(sender, instance, **kwargs):
    """Supprime le fichier physique lors de la suppression de la Story"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


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
