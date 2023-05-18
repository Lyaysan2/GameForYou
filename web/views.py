from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from web.forms import RegistrationForm, AuthForm, SystemCharForm
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
            print(form)
            print(form.cleaned_data)
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
