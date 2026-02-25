from django.db import models

class Quote(models.Model):
    text = models.TextField(verbose_name="Citation")
    author = models.CharField(max_length=255, verbose_name="Auteur & Manga")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Citation"
        verbose_name_plural = "Citations"

    def __str__(self):
        return f'"{self.text[:50]}..." - {self.author}'
