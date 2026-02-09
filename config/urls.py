"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home_view, login_view, register_view, logout_view

urlpatterns = [
    path('', home_view, name='home'),
    path('', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('reader/', include('reader.urls')),
    path('catalogue/', include('catalog.urls')),
    path('connexion/', login_view, name='login'),
    path('inscription/', register_view, name='register'),
    path('deconnexion/', logout_view, name='logout'),
    path('users/', include('users.urls')),
    path('forum/', include('social.urls')),
    path('admin-panel/', include('administration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
