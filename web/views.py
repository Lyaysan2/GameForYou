import pandas as pd
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from web.forms import RegistrationForm, AuthForm, SystemCharForm, SimilarGameForm
from web.ml import recommend_game
from web.models import SystemCharacteristics, Game

User = get_user_model()


def main_view(request):
    return render(request, 'web/main.html')


def registration_view(request):
    form = RegistrationForm()
    is_success = False
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password'])
            user.save()
            is_success = True
    return render(request, 'web/registration.html', {'form': form, 'is_success': is_success})


def auth_view(request):
    form = AuthForm()
    if request.method == 'POST':
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is None:
                form.add_error(None, 'Введены неверные данные')
            else:
                login(request, user)
                return redirect('main')
    return render(request, 'web/auth.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('main')


@login_required
def syst_char_add_view(request):
    form = SystemCharForm()
    if request.method == 'POST':
        form = SystemCharForm(data=request.POST, initial={'user': request.user})
        if form.is_valid():
            form.save()
            return redirect('main')
    return render(request, 'web/syst_char_form.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    syst_char_list = SystemCharacteristics.objects.all().filter(user=user)
    favourite_games = Game.objects.all().filter(users=user)
    return render(request, 'web/profile.html', {'user': user,
                                                'syst_char_list': syst_char_list,
                                                'favourite_games': favourite_games})


@login_required
def syst_char_delete_view(request, id):
    syst_char = get_object_or_404(SystemCharacteristics, user=request.user, id=id)
    syst_char.delete()
    return redirect('profile')


@login_required
def favourite_game_delete_view(request, id):
    favourite_game = get_object_or_404(Game, users=request.user, id=id)
    favourite_game.users.clear()
    return redirect('profile')


@login_required
def favourite_game_add_view(request, id):
    game = get_object_or_404(Game, id=id)
    user = request.user
    game.users.add(user)
    return redirect('similar_games')


@login_required
def similar_games_view(request):
    form = SimilarGameForm(request.GET or None)
    user = request.user
    games = []
    if form.is_valid():
        selected_game = get_object_or_404(Game, id=form.cleaned_data['name'])
        similar_games = recommend_game(selected_game.name)[['name', 'link']].values.tolist()
        similar_games = similar_games
        for game in similar_games:
            found_game = Game.objects.filter(name=game[0]).first()
            if found_game is not None:
                games.append(found_game)

    return render(request, 'web/similar_games.html', {'form': form, 'similar_games': games, 'user': user})

