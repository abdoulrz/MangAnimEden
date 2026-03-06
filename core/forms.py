from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nom", widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Votre nom'
    }))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'form-control', 
        'placeholder': 'votre.email@exemple.com'
    }))
    subject = forms.CharField(max_length=200, label="Sujet", widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Sujet de votre message'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 
        'rows': 5, 
        'placeholder': 'Comment pouvons-nous vous aider ?'
    }), label="Message")
