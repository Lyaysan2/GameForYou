from django.urls import path, include

from web.views import main_view, registration_view, auth_view, logout_view, syst_char_add_view, profile_view, \
    syst_char_delete_view, favourite_game_delete_view, similar_games_view

urlpatterns = [
    path('', main_view, name='main'),
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),
    path('syst/add', syst_char_add_view, name='syst_char_add'),
    path('select2/', include('django_select2.urls')),
    path('profile/', profile_view, name='profile'),
    path('syst_char/<int:id>/delete', syst_char_delete_view, name='syst_char_delete'),
    path('favourite_game_delete/<int:id>/delete', favourite_game_delete_view, name='favourite_game_delete'),
    path('similar_games/', similar_games_view, name='similar_games'),
]
