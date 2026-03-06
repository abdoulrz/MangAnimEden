from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import os

class ChunkedUpload(models.Model):
    STATUS_CHOICES = [
        ('uploading', 'En cours'),
        ('processing', 'Assemblage'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    upload_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    filename = models.CharField(max_length=255)
    total_chunks = models.IntegerField()
    received_chunks = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Progress tracking for extraction
    total_files_to_process = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)

    def get_temp_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'temp_uploads', str(self.upload_id))

    class Meta:
        verbose_name = "Upload par morceaux"
        verbose_name_plural = "Uploads par morceaux"

    def __str__(self):
        return f"{self.filename} ({self.status})"

class SystemLog(models.Model):
    ACTION_TYPES = [
        ('USER_BAN', 'Bannissement Utilisateur'),
        ('USER_UNBAN', 'Débannissement Utilisateur'),
        ('USER_PROMOTE', 'Promotion Utilisateur'),
        ('USER_DEMOTE', 'Rétrogradation Utilisateur'),
        ('CONTENT_DELETE', 'Suppression Contenu'),
        ('GROUP_BAN', 'Bannissement Groupe'),
        ('GROUP_CLOSE', 'Fermeture Groupe'),
        ('GENRE_CREATE', 'Création Genre'),
        ('GENRE_UPDATE', 'Modification Genre'),
        ('SERIES_CREATE', 'Création Série'),
        ('SERIES_UPDATE', 'Modification Série'),
        ('CHAPTER_CREATE', 'Création Chapitre'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actions_performed',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Auteur"
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actions_received',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cible (Utilisateur)"
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name="Action")
    details = models.TextField(blank=True, verbose_name="Détails")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log Système"
        verbose_name_plural = "Logs Système"

    def __str__(self):
        return f"[{self.get_action_display()}] {self.actor} -> {self.details[:50]}"

class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam ou publicité'),
        ('harassment', 'Harcèlement ou discours de haine'),
        ('inappropriate', 'Contenu inapproprié'),
        ('copyright', 'Violation de droit d\'auteur'),
        ('other', 'Autre')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('resolved', 'Résolu'),
        ('dismissed', 'Rejeté')
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reports_submitted',
        verbose_name="Signaleur"
    )
    
    # Generic Relation
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_type', 'target_id')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name="Raison")
    description = models.TextField(blank=True, verbose_name="Détails supplémentaires")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de résolution")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_resolved',
        verbose_name="Modérateur"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def __str__(self):
        return f"Signalement {self.get_reason_display()} par {self.reporter} ({self.get_status_display()})"
