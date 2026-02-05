from django.db import models
from django.conf import settings

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='group_icons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

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
