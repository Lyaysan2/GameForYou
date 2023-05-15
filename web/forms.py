from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm, Form
from django_select2 import forms as s2forms

from web.models import SystemCharacteristics

User = get_user_model()


class RegistrationForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['password2']:
            self.add_error('password', 'Пароли не совпадают')
        return cleaned_data

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')


class AuthForm(Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class OSWidget(s2forms.Select2Widget):
    search_fields = [
        "os__icontains",
    ]


class ProcessorWidget(s2forms.Select2Widget):
    search_fields = [
        "processor__icontains",
    ]


class GraphicsWidget(s2forms.Select2Widget):
    search_fields = [
        "graphics__icontains",
    ]


class DirectxWidget(s2forms.Select2Widget):
    search_fields = [
        "directx__icontains",
    ]


class SystemCharForm(ModelForm):
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = SystemCharacteristics
        fields = ('os', 'processor', 'memory', 'graphics', 'directx', 'storage')
        widgets = {
            'os': OSWidget,
            'processor': ProcessorWidget,
            'graphics': GraphicsWidget,
            'directx': DirectxWidget,
        }
