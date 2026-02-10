from django import forms
from catalog.models import Chapter
class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['series', 'number', 'title', 'source_file']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 10.5'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Titre du chapitre (optionnel)'}),
            'series': forms.HiddenInput(),
        }
        labels = {
            'source_file': 'FICHIER',
            'number': 'NUMÉRO DU CHAPITRE',
            'title': 'TITRE (OPTIONNEL)',
        }

from catalog.models import Series
# Import MultipleFileInput from catalog.series_forms to reuse widget
from catalog.series_forms import MultipleFileInput

class SeriesForm(forms.ModelForm):
    # folder_upload removed from here to be handled manually in template to avoid validation issues

    class Meta:
        model = Series
        fields = ['title', 'slug', 'description', 'cover', 'type', 'genres', 'author', 'artist', 'status', 'release_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la série'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Slug (auto-généré si vide)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'artist': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genres': forms.CheckboxSelectMultiple(),
        }
