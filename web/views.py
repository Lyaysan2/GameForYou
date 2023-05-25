from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from web.forms import RegistrationForm, AuthForm, SystemCharForm, SimilarGameForm, TagFilterForm
from web.ml import get_games_by_PC, recommend_game, get_tags_list_choices, get_filtered_games
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
            return redirect('profile')
    return render(request, 'web/syst_char_form.html', {'form': form})


@login_required
@cache_page(3600)
def profile_view(request):
    user = request.user
    syst_char_list = SystemCharacteristics.objects.all().filter(user=user)
    favourite_games = Game.objects.all().filter(users=user)
    for i in range(len(favourite_games)):
        favourite_games[i].developer = favourite_games[i].developer.split(', ')
        favourite_games[i].tags = favourite_games[i].tags.split(', ')
        favourite_games[i].ram = get_review_color(favourite_games[i])
    total_count = len(favourite_games)
    page_number = request.GET.get("page", 1)
    paginator = Paginator(favourite_games, per_page=7)
    return render(request, 'web/profile.html', {'user': user,
                                                'syst_char_list': syst_char_list,
                                                'favourite_games': paginator.get_page(page_number),
                                                'total_count': total_count})


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
    return redirect('profile')


@login_required
@cache_page(3600)
def similar_games_view(request):
    form = SimilarGameForm(request.GET or None)
    user = request.user
    similar_games = None
    if form.is_valid():
        if form.cleaned_data['name']:
            selected_game = get_object_or_404(Game, id=form.cleaned_data['name'])
            similar_games_df = recommend_game(selected_game.name)
            similar_games = []
            if similar_games_df is not None:
                similar_games_df = similar_games_df[['id']].values.tolist()
                for game in similar_games_df:
                    found_game = Game.objects.filter(id=game[0]).first()
                    if found_game is not None:
                        found_game.developer = found_game.developer.split(', ')
                        found_game.tags = found_game.tags.split(', ')
                        found_game.ram = get_review_color(found_game)
                        similar_games.append(found_game)
                total_count = len(similar_games)
                page_number = request.GET.get("page", 1)
                paginator = Paginator(similar_games, per_page=7)
                return render(request, 'web/similar_games.html',
                              {'form': form, 'similar_games': paginator.get_page(page_number), 'user': user,
                               'total_count': total_count, 'selected_game_id': selected_game.id})
    return render(request, 'web/similar_games.html', {'form': form, 'similar_games': similar_games, 'user': user})


@login_required()
@cache_page(3600)
def syst_char_games_view(request):
    syst_char_by_user = SystemCharacteristics.objects.all().filter(user=request.user)
    selected_syst_char = None
    games = None
    if len(request.GET) != 0:
        selected_syst_char = get_object_or_404(SystemCharacteristics, id=request.GET['syst_char'])

        games_df = get_games_by_PC(str(float(selected_syst_char.os.replace('Windows ', ''))),
                                   selected_syst_char.processor,
                                   selected_syst_char.graphics,
                                   selected_syst_char.directx,
                                   int(selected_syst_char.ram) * 1024)
        games = []
        if not games_df.empty:
            games_df = games_df[
                ['name']].values.tolist()
            for game in games_df:
                found_game = Game.objects.filter(name=game[0]).first()
                found_game.developer = found_game.developer.split(', ')
                found_game.tags = found_game.tags.split(', ')
                if found_game is not None:
                    games.append(found_game)

        total_count = len(games)
        page_number = request.GET.get("page", 1)
        paginator = Paginator(games, per_page=7)
        return render(request, 'web/syst_char_games.html', {'syst_char_by_user': syst_char_by_user,
                                                            'selected_syst_char': selected_syst_char,
                                                            'games': paginator.get_page(page_number),
                                                            'user': request.user,
                                                            'total_count': total_count})

    return render(request, 'web/syst_char_games.html', {'syst_char_by_user': syst_char_by_user,
                                                        'selected_syst_char': selected_syst_char,
                                                        'games': games,
                                                        'user': request.user})


@cache_page(3600)
def game_filter_view(request):
    games = []
    choices = get_tags_list_choices()
    form = TagFilterForm(request.GET, choices)
    form.is_valid()

    convert = lambda i: eval(i) if i != '' else None
    games_df = get_filtered_games(price_asc=convert(form.cleaned_data['price']),
                                  date_asc=convert(form.cleaned_data['date']),
                                  popularity_asc=convert(form.cleaned_data['popularity']),
                                  tags=form.cleaned_data['tags']).values.tolist()[:40]
    for game in games_df:
        found_game = Game.objects.filter(id=game[0]).first()
        if found_game is not None:
            found_game.developer = found_game.developer.split(', ')
            found_game.tags = found_game.tags.split(', ')
            found_game.ram = get_review_color(found_game)
            games.append(found_game)

    page_number = request.GET.get("page", 1)
    paginator = Paginator(games, per_page=7)
    total_count = len(games)
    return render(request, 'web/game_filter.html', {'form': form, 'games': paginator.get_page(page_number),
                                                        'total_count': total_count, 'selected_filters': form.cleaned_data})


def get_review_color(game):
    revies_list = (('Very Positive', 'Overwhelmingly Positive', 'Mostly Positive', 'Positive'), \
                  ('Mixed'), \
                  ('Mostly Negative', 'Overwhelmingly Negative', 'Negative', 'Very Negative'),\
                  ('9 user reviews', '8 user reviews', '7 user reviews', '6 user reviews', '5 user reviews',
                   '4 user reviews', '3 user reviews', '2 user reviews', '1 user reviews', 'No user reviews'))
    ram = None

    if game.reviews in revies_list[0]:
        ram = '#23FD10'
    elif game.reviews in revies_list[1]:
        ram = '#FDBB10'
    elif game.reviews in revies_list[2]:
        ram = '#FD1057'
    elif game.reviews in revies_list[3]:
        ram = '#939AB0'
    return ram