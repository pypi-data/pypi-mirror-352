"""
URL configuration for doc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from backend.views import index, catalog, profile_page, create_reservation, reservations, user_login, registration, catalog_detail

urlpatterns = [
    path('', index, name='index'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    path('catalog/<int:id>/', catalog_detail, name='catalog_detail'),
    path('catalog/', catalog, name='catalog'),
    path('profile/', profile_page, name='profile'),
    path('create_reservation/', create_reservation, name='create_reservation'),
    path('reservations/', reservations, name='reservations'),
    path('user_login/', user_login, name='login'),
    path('registration/', registration, name='registration'),
    path('logout/', LogoutView.as_view(template_name='login.html'), name='logout'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
