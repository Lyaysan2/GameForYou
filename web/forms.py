from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm, Form, CheckboxSelectMultiple
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2Widget, ModelSelect2Mixin

from web.models import SystemCharacteristics, Game

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


class GameNameWidget(ModelSelect2Widget):
    queryset = Game.objects.all()
    search_fields = [
        'name__icontains',
    ]


class TagsWidget(s2forms.Select2MultipleWidget):
    search_fields = [
        "tags__icontains",
    ]


class SystemCharForm(ModelForm):
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = SystemCharacteristics
        fields = ('os', 'processor', 'ram', 'graphics', 'directx', 'storage')
        widgets = {
            'os': OSWidget,
            'processor': ProcessorWidget,
            'graphics': GraphicsWidget,
            'directx': DirectxWidget,
        }


class SimilarGameForm(ModelForm):
    class Meta:
        model = Game
        fields = ('name',)
        widgets = {
            'name': GameNameWidget,
        }


class GameFilterForm(Form):
    price = forms.ChoiceField(choices=(('asc', 'Цена по возрастанию'), ('desc', 'Цена по убыванию'), ('default', 'Выберите опцию')))


class TagFilterForm(Form):
    CHOICES = (('afff', 'afffffffffff'),
               ('baa', 'baa'),
               ('bca', 'bca'),
               ('bui', 'bui'),
               ('c', 'c'),
               ('d', 'd'),)
    tags = forms.MultipleChoiceField(choices=CHOICES, widget=TagsWidget)
