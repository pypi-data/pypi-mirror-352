from django.contrib import admin
from . import models


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'FIO', 'phone')


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time', 'description', 'status')
    list_filter = ('date', 'status')


@admin.register(models.CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ('name',)
