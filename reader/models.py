from django.db import models
from django.conf import settings


class UnlockedChapter(models.Model):
    """
    Sert de registre pour les chapitres premium débloqués par l'utilisateur.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='unlocked_chapters',
        verbose_name="Utilisateur"
    )
    chapter = models.ForeignKey(
        'catalog.Chapter',
        on_delete=models.CASCADE,
        related_name='unlocked_by',
        verbose_name="Chapitre"
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chapitre Débloqué"
        verbose_name_plural = "Chapitres Débloqués"
        unique_together = ['user', 'chapter']
    
    def __str__(self):
        return f"{self.user.nickname} a débloqué {self.chapter}"


class ReadingProgress(models.Model):
    """
    Suit la progression de lecture d'un utilisateur.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_progress',
        verbose_name="Utilisateur"
    )
    chapter = models.ForeignKey(
        'catalog.Chapter',
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name="Chapitre"
    )
    current_page = models.PositiveIntegerField(
        default=1,
        verbose_name="Page actuelle"
    )
    completed = models.BooleanField(default=False, verbose_name="Terminé")
    
    last_read = models.DateTimeField(auto_now=True, verbose_name="Dernière lecture")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.nickname} - {self.chapter}"
    
    class Meta:
        verbose_name = "Progression de lecture"
        verbose_name_plural = "Progressions de lecture"
        unique_together = ['user', 'chapter']
        ordering = ['-last_read']
