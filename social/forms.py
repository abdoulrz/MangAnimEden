from .models import Group, Event
from django import forms

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du groupe'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description du groupe'}),
            'icon': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'événement'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description...'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu (optionnel)'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
