from django.db import models
from django.conf import settings  # Import settings for AUTH_USER_MODEL
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
import shutil

def page_image_upload_path(instance, filename):
    """
    Génère un chemin logique pour les images de pages :
    scans_pages/<series_slug>/chapter_<number>/<filename>
    """
    series_slug = instance.chapter.series.slug
    chapter_num = instance.chapter.number
    return f'scans_pages/{series_slug}/chapter_{chapter_num}/{filename}'




class Genre(models.Model):
    """
    Représente un genre de manga (Action, Aventure, etc.)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['name']


class Series(models.Model):

    """
    Représente une série de manga/manhwa/manhua.
    """
    TYPE_CHOICES = [
        ('manga', 'Manga'),
        ('manhwa', 'Manhwa'),
        ('manhua', 'Manhua'),
        ('novel', 'Novel'),
        ('webtoon', 'Webtoon'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    cover = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="Couverture")
    
    # Métadonnées
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='manga', verbose_name="Type")
    genres = models.ManyToManyField(Genre, blank=True, verbose_name="Genres", related_name='series')
    nsfw = models.BooleanField(default=False, verbose_name="Contenu 18+ (NSFW)")
    author = models.CharField(max_length=200, blank=True, verbose_name="Auteur")
    artist = models.CharField(max_length=200, blank=True, verbose_name="Artiste")
    status = models.CharField(
        max_length=20,
        choices=[
            ('ongoing', 'En cours'),
            ('completed', 'Terminé'),
            ('hiatus', 'En pause'),
        ],
        default='ongoing',
        verbose_name="Statut"
    )
    release_date = models.DateField(blank=True, null=True, verbose_name="Date de publication")
    
    # Analytics
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues", db_index=True)
    average_rating = models.FloatField(default=0.0, verbose_name="Note moyenne", db_index=True)
    chapters_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de chapitres", db_index=True)
    review_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'avis", db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def update_metadata(self):
        """
        Recalculates average_rating, chapters_count, and review_count and saves.
        """
        from django.db.models import Avg
        self.average_rating = round(self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0, 1)
        self.chapters_count = self.chapters.count()
        self.review_count = self.reviews.count()
        self.save(update_fields=['average_rating', 'chapters_count', 'review_count'])
    
    @property
    def get_review_count(self):
        return self.reviews.count()

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Série"
        verbose_name_plural = "Séries"
        ordering = ['-updated_at']


class Chapter(models.Model):
    """
    Représente un chapitre d'une série.
    """
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name="Série"
    )
    number = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        verbose_name="Numéro"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    source_file = models.FileField(upload_to='scans/', blank=True, null=True, verbose_name="Fichier Source")
    is_premium = models.BooleanField(default=False, verbose_name="Chapitre Premium")
    
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def is_pdf(self):
        """Checks if the source file is a PDF."""
        return self.source_file and self.source_file.name.lower().endswith('.pdf')

    def __str__(self):
        return f"{self.series.title} - Chapitre {self.number}"
    
    class Meta:
        verbose_name = "Chapitre"
        verbose_name_plural = "Chapitres"
        ordering = ['series', 'number']
        unique_together = ['series', 'number']


class Page(models.Model):
    """
    Représente une page d'un chapitre.
    """
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='pages',
        verbose_name="Chapitre"
    )
    page_number = models.PositiveIntegerField(verbose_name="Numéro de page")
    image = models.ImageField(
        upload_to=page_image_upload_path,
        verbose_name="Image"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.chapter} - Page {self.page_number}"
    
    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['chapter', 'page_number']
        unique_together = ['chapter', 'page_number']


class Favorite(models.Model):
    """
    Modèle pour les favoris utilisateur.
    Relie un utilisateur à une série.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'series')
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} ❤️ {self.series}"


# --- SIGNALS FOR AUTO-DELETING FILES ---

@receiver(post_delete, sender=Series)
def auto_delete_series_assets_on_delete(sender, instance, **kwargs):
    """Deletes all associated assets (cover and scans folder) when the Series is deleted."""
    # 1. Delete Cover Image
    if instance.cover:
        try:
            instance.cover.delete(save=False)
        except Exception:
            pass
            
    # 2. Delete the entire series folder in scans_pages
    if instance.slug:
        series_path = os.path.join(settings.MEDIA_ROOT, 'scans_pages', instance.slug)
        if os.path.exists(series_path):
            try:
                shutil.rmtree(series_path)
            except Exception:
                pass

@receiver(post_delete, sender=Chapter)
def auto_delete_chapter_assets_on_delete(sender, instance, **kwargs):
    """Deletes source file and the entire chapter folder when a Chapter is deleted."""
    # 1. Delete source archive/pdf
    if instance.source_file:
        try:
            instance.source_file.delete(save=False)
        except Exception:
            pass
            
    # 2. Delete the chapter folder containing extracted pages
    try:
        series_slug = instance.series.slug
        chapter_dir = os.path.join(settings.MEDIA_ROOT, 'scans_pages', series_slug, f'chapter_{instance.number}')
        if os.path.exists(chapter_dir):
            shutil.rmtree(chapter_dir)
    except Exception:
        pass

@receiver(post_delete, sender=Page)
def auto_delete_page_image_on_delete(sender, instance, **kwargs):
    """Deletes the specific page image file, directory cleanup handled by Chapter/Series delete."""
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            pass


class Review(models.Model):
    """
    Modèle d'Avis et de Note pour une série.
    """
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=0, verbose_name="Note") # 1 to 5
    content = models.TextField(blank=True, verbose_name="Avis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('series', 'user')
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.nickname} - {self.series.title} ({self.rating}/5)"


# --- SIGNALS FOR DENORMALIZATION ---

@receiver([models.signals.post_save, models.signals.post_delete], sender=Chapter)
def update_series_chapters_count(sender, instance, **kwargs):
    """Updates chapters_count on Series when a Chapter is created or deleted."""
    if instance.series:
        instance.series.chapters_count = instance.series.chapters.count()
        instance.series.save(update_fields=['chapters_count'])

@receiver([models.signals.post_save, models.signals.post_delete], sender=Review)
def update_series_average_rating(sender, instance, **kwargs):
    """Updates average_rating and review_count on Series when a Review is created or deleted."""
    if instance.series:
        from django.db.models import Avg
        avg = instance.series.reviews.aggregate(Avg('rating'))['rating__avg']
        instance.series.average_rating = round(avg or 0.0, 1)
        instance.series.review_count = instance.series.reviews.count()
        instance.series.save(update_fields=['average_rating', 'review_count'])
