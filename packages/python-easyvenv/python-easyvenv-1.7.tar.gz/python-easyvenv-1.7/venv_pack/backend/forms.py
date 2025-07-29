from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from backend import models


class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Reservation
        fields = ['phone', 'date', 'time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7(XXX)-XXX-XX-XX',
                'class': 'form-control'
            }),
        }


class CreateUserForm(UserCreationForm):
    username_validator = RegexValidator(r'[a-zA-Z0-9\s-]',
                                        'Используйте латиницу, цифры, пробелы или тире')

    password_validator = RegexValidator(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
        'Пароль должен содержать минимум 8 символов, включая буквы и цифры')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.append(self.username_validator)
        self.fields['password1'].validators.append(self.password_validator)
        for field in ['username', 'email', 'password1']:
            self.fields[field].required = True

    class Meta:
        model = User
        fields = ['username', 'email', 'password1']
        widgets = {
            'password1': forms.PasswordInput(),
        }


class CreateProfileForm(forms.ModelForm):
    name_validator = RegexValidator(r'[а-яА-Я\s]',
                                    'Используйте кириллицу и пробелы')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['FIO'].validators.append(self.name_validator)
        for field in ['FIO', 'phone']:
            self.fields[field].required = True

    class Meta:
        model = models.UserProfile
        fields = ['FIO', 'phone']


class LoginForm(AuthenticationForm):
    pass


class AddItemForm(forms.ModelForm):
    class Meta:
        model = models.CatalogItem
        fields = ['name', 'image']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email',]


class UserProfileUpdateForm(forms.ModelForm):
    FIO = forms.CharField(label='ФИО', max_length=100, required=False)
    phone = forms.CharField(label='Телефон', max_length=20, required=False)

    class Meta:
        model = models.UserProfile
        fields = ['FIO', 'phone']

    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['FIO'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})