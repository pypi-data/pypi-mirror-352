from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Application

class RegisterForm(UserCreationForm):
    gal = forms.BooleanField(
        label='Согласие с правилами', required=True, error_messages={'required': 'Вы должны принять правила'})
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'middle_name',
            'snils', 'phone', 'gal'
        ]
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин или Email')

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = []