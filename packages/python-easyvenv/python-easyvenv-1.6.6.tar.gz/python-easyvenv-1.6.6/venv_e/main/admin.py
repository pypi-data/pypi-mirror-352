from django.contrib import admin
from .models import CustomUser, Naprav, Application


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'last_name', 'first_name', 'email')


@admin.register(Naprav)
class NapravAdmin(admin.ModelAdmin):
    list_display = ('cod', 'name', 'obl', 'year', 'budget')


@admin.register(Application)
class Appplications(admin.ModelAdmin):
    list_display = ('id', 'user', 'direction', 'created_at', 'status')



