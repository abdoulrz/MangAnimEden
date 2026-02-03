from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_index, name='index'),
    path('detail/', views.manga_detail, name='detail'),
]
