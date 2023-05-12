from django.urls import path, include

from web.views import main_view, registration_view, auth_view, logout_view, syst_char_add_view

urlpatterns = [
    path('', main_view, name='main'),
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),
    path('syst/add', syst_char_add_view, name='syst_char_add'),
    # re_path(r'^city-autocomplete/$', OSAutocomplete.as_view(), name='city-autocomplete'),
    path("select2/", include("django_select2.urls")),
]
