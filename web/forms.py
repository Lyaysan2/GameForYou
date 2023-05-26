from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm, Form
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2Widget

from web.ml import get_tags_list_choices
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


class BaseAutocompleteModelSelect(s2forms.ModelSelect2Widget):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "width: 800px"}

    def build_attrs(self, base_attrs, extra_attrs=None):
        base_attrs = super().build_attrs(base_attrs, extra_attrs)
        base_attrs.update(
            {"data-minimum-input-length": 0, "data-placeholder": self.empty_label}
        )
        return base_attrs


class GameNameWidget(BaseAutocompleteModelSelect):
    empty_label = "Выберите игру"
    queryset = Game.objects.order_by('-popularity')
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


class TagFilterForm(Form):
    def __init__(self, *args, **kwargs):
        self.choices = args[1]
        super(TagFilterForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.MultipleChoiceField(choices=self.choices, widget=TagsWidget, required=False)
    price = forms.ChoiceField(choices=[(None, 'default'), (True, 'По возрастанию цены'), (False, 'По убыванию цены')], required=False)
    date = forms.ChoiceField(choices=[(None, 'default'), (False, 'Сначала новые'), (True, 'Сначала старые')], required=False)
    popularity = forms.ChoiceField(choices=[(None, 'default'), (False, 'Сначала популярные'), (True, 'Сначала непопулярные')], required=False)
