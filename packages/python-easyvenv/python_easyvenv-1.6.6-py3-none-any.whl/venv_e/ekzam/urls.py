from django.contrib import admin
from django.urls import path, include
from main.views import index  # Импортируем index view

urlpatterns = [
    path('manage/', admin.site.urls),
    path('', index, name='index'),
    path('', include('main.urls')),
]