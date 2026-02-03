from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='social_home'),
]
