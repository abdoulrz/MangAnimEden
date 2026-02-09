from django import forms
from .models import Series

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class SeriesAdminForm(forms.ModelForm):
    folder_upload = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'webkitdirectory': True, 'multiple': True}),
        # widget=forms.TextInput(attrs={'placeholder': 'DEBUG: Should allow folder upload'}),
        label="Dossier",
        help_text="Sélectionnez un dossier contenant les fichiers des chapitres (cbz, zip, pdf, epub) pour les importer automatiquement."
    )

    class Meta:
        model = Series
        fields = '__all__'
