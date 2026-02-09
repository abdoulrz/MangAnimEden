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
