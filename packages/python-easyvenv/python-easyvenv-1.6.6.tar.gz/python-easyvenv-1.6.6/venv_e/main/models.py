from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUser(AbstractUser):
    middle_name = models.CharField(max_length=150, verbose_name='Отчество', blank=True)
    snils = models.CharField(max_length=11, verbose_name='СНИЛС', unique=True)
    phone = models.CharField(max_length=11, verbose_name='Телефон')
    gal = models.BooleanField(default=False, verbose_name='Согласие с правилами')
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'snils', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Naprav(models.Model):
    cod = models.CharField(max_length=50, verbose_name='Код')
    name = models.CharField(max_length=150, verbose_name='наименование')
    obl = models.CharField(max_length=150, verbose_name='область знаний')
    year = models.CharField(max_length=10, verbose_name='Срок обучения')
    budget = models.CharField(max_length=20, verbose_name='бюджетные места')

    def __str__(self):
        return self.name


class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    direction = models.ForeignKey(Naprav, on_delete=models.CASCADE, verbose_name='Направление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи')
    status = models.CharField(max_length=20, default='На рассмотрении', verbose_name='Статус')

    def __str__(self):
        return f"Заявка {self.user.username} на {self.direction.name}"
