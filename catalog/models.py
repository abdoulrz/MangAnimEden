from django.db import models
from django.conf import settings  # Import settings for AUTH_USER_MODEL
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

def page_image_upload_path(instance, filename):
    """
    Génère un chemin logique pour les images de pages :
    mangas/<series_slug>/chapter_<number>/<filename>
    """
    series_slug = instance.chapter.series.slug
    chapter_num = instance.chapter.number
    return f'mangas/{series_slug}/chapter_{chapter_num}/{filename}'




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
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    
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





