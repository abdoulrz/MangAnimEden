from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('nickname', 'email')
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'input auth-input', 'placeholder': 'VotrePseudo'}),
            'email': forms.EmailInput(attrs={'class': 'input auth-input', 'placeholder': 'vous@exemple.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add widget classes to password fields added by UserCreationForm
        for field in self.fields:
            if 'password' in field:
                self.fields[field].widget.attrs.update({'class': 'input auth-input', 'placeholder': '••••••••'})

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Adresse email', 
        widget=forms.TextInput(attrs={'class': 'input auth-input', 'placeholder': 'vous@exemple.com'})
    )
    password = forms.CharField(
        label='Mot de passe', 
        widget=forms.PasswordInput(attrs={'class': 'input auth-input', 'placeholder': '••••••••'})
    )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'nickname', 'avatar', 'bio',
            'social_facebook', 'social_twitter', 'social_instagram', 'social_youtube', 'social_linkedin',
            'location_country', 'location_city'
        ]
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'input profile-input', 'placeholder': 'Votre pseudo'}),
            'avatar': forms.FileInput(attrs={'class': 'file-input-hidden'}),
            'bio': forms.Textarea(attrs={'class': 'input profile-textarea', 'placeholder': 'Parlez-nous de vous...', 'rows': 4}),
            'location_country': forms.TextInput(attrs={'class': 'input profile-input', 'placeholder': 'Votre pays'}),
            'location_city': forms.TextInput(attrs={'class': 'input profile-input', 'placeholder': 'Votre ville'}),
            'social_facebook': forms.URLInput(attrs={'class': 'input profile-input', 'placeholder': 'https://facebook.com/...'}),
            'social_twitter': forms.URLInput(attrs={'class': 'input profile-input', 'placeholder': 'https://twitter.com/...'}),
            'social_instagram': forms.URLInput(attrs={'class': 'input profile-input', 'placeholder': 'https://instagram.com/...'}),
            'social_youtube': forms.URLInput(attrs={'class': 'input profile-input', 'placeholder': 'https://youtube.com/...'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'input profile-input', 'placeholder': 'https://linkedin.com/in/...'}),
        }
