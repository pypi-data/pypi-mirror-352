from django.urls import path
from . import views
from .views import catalog, documents

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('catalog/', catalog, name='catalog'),
    path('documents/', documents, name='documents'),
    path('naprav/<int:pk>', views.naprav_detail, name='naprav_detail')
]