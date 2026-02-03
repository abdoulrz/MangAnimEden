from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profil/', views.profile_view, name='profile'),
    path('profil/modifier/', views.edit_profile_view, name='edit_profile'),
]
