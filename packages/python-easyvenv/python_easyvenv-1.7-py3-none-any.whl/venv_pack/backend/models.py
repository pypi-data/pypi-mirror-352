from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    FIO = models.CharField(max_length=100, verbose_name='ФИО')
    phone = models.CharField(max_length=17, verbose_name='Телефон')

    def __str__(self):
        return f"Профиль {self.user.username}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, verbose_name='Номер телефона', blank=True, null=True)
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    description = models.TextField(verbose_name='Комментарий', blank=True, null=True)
    comment = models.TextField(verbose_name='Причина отказа', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new', verbose_name='Статус')

    def __str__(self):
        return f'{self.user} {self.date} {self.time}'


class CatalogItem(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(verbose_name='Изображение', blank=True, null=True)
    price = models.FloatField(verbose_name='Цена', blank=True, null=True)
