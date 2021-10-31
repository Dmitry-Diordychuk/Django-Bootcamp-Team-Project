from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader

import logging

from game.data_manager import DataManager
from game.save_manager import SaveManager

logger = logging.getLogger(__name__)
game_manager = DataManager()
save_manager = SaveManager()

# Create your views here.
def index(request):
    if request.method == "POST":
        save_manager.update_files()
        if request.POST.get('A'):
            game_manager.load_default_settings()
            return redirect('/worldmap')
        elif request.POST.get('B'):
            return redirect('options/load_game')

    return render(request, 'moviemon/title_screen.html', {})


def worldmap(request):
    if request.method == "POST":
        if request.POST.get('start'):
            return redirect('/options')
        elif request.POST.get('select'):
            return redirect('/moviedex')
        elif game_manager.isMoviemonEncountered:
            if request.POST.get('A'):
                game_manager.isMoviemonEncountered = False
                moviemon_id = game_manager.get_random_movie()
                return redirect('/battle/' + moviemon_id)
        elif game_manager.isMovieballFound:
            if request.POST.get('A'):
                game_manager.isMovieballFound = False
                game_manager.pick_movieball()
        else:
            if request.POST.get('left.x'):
                game_manager.go('left')
            elif request.POST.get('right.x'):
                game_manager.go('right')
            elif request.POST.get('up.x'):
                game_manager.go('up')
            elif request.POST.get('down.x'):
                game_manager.go('down')

    context = {
        'frame': game_manager.get_frame(),
        'movieballs': game_manager.player_movieballs,
        'isMoviemonEncountered': game_manager.isMoviemonEncountered,
        'isMovieballFound': game_manager.isMovieballFound
    }
    return render(request, 'moviemon/worldmap.html', context)


def battle(request, moviemon_id=None):
    movie = game_manager.get_movie(moviemon_id)
    movie_poster_url = movie["Poster"]

    if request.method == "POST":
        if game_manager.isMovieballThrown:
            if game_manager.isMoviemonCatched:
                if request.POST.get('B'):
                    game_manager.isMovieballThrown = False
                    game_manager.isMoviemonCatched = False
                    return redirect('/worldmap')
            else:
                if request.POST.get('A'):
                    game_manager.isMovieballThrown = False
                    game_manager.isMoviemonCatched = False
        else:
            if request.POST.get('A') and game_manager.player_movieballs > 0:
                game_manager.isMovieballThrown = True
                if game_manager.throw_movieball(moviemon_id):
                    game_manager.isMoviemonCatched = True
            elif request.POST.get('B'):
                return redirect('/worldmap')

    context = {
        "moviemon_img_url": movie_poster_url,
        "player_strength": game_manager.player_strength,
        "moviemon_strength": round(float(movie["imdbRating"])),
        "movieballs": game_manager.player_movieballs,
        'winrate': game_manager.calculate_chance(moviemon_id),
        "isMovieballThrown": game_manager.isMovieballThrown,
        "isMoviemonCatched": game_manager.isMoviemonCatched
    }
    return render(request, 'moviemon/battle.html', context)


def moviedex(request):
    select = 0
    moviemons_num = len(game_manager.captured_moviemons)
    if request.POST.get('select'):
        return redirect('/worldmap')
    elif request.POST.get('down.x'):
        select = select + 1 if select < moviemons_num else select
    elif request.POST.get('up.x'):
        select = select - 1 if select > 0 else select

    if moviemons_num == 0:
        return render(request, 'moviemon/moviedex.html', {"moviedex": []})
    else:
        moviemons = [(moviemon["Title"], moviemon['imdbID']) for moviemon in game_manager.captured_moviemons]
    context = {"moviedex": moviemons, 'select': select}
    return render(request, 'moviemon/moviedex.html', context)


def detail(request):
    if request.method == "POST":
        if request.POST.get('B'):
            return redirect('/moviedex')
    imdb = request.GET.get('imdb')
    moviemon = {}
    for a in game_manager.captured_moviemons:
        if a['imdbID'] == imdb:
            moviemon = ({
                'Title': a['Title'],
                'Year': a['Year'],
                'Genre': a['Genre'],
                'Director': a['Director'],
                'Actors': a['Actors'],
                'Plot': a['Plot'],
                'Country': a['Country']
            }, a['Poster'])
    context = {'moviemon': moviemon}
    return render(request, 'moviemon/detail.html', context)


def options(request):
    if request.method == "POST":
        if request.POST.get('start'):
            return redirect('/worldmap')
        elif request.POST.get('A'):
            return redirect('options/save_game')
        elif request.POST.get('B'):
            return redirect('/')
    context = {}
    return render(request, 'moviemon/options.html', context)


def load(request):
    global game_manager
    save_manager.update_files
    a_purpose = 'Load'
    if request.method == "POST":
        if request.POST.get('A'):
            if game_manager.isGameLoaded == True:
                game_manager.isGameLoaded = False
                return redirect('/worldmap')
            slot = None
            if game_manager.selected == 1:
                slot = 'a'
            elif game_manager.selected == 2:
                slot = 'b'
            elif game_manager.selected == 3:
                slot = 'c'
            data = save_manager.load(slot)
            if data != None:
                game_manager = DataManager(data)
                game_manager = game_manager.load()
                game_manager.isGameLoaded = True
        elif request.POST.get('B'):
            game_manager.selected = 1
            return redirect('/')
        elif request.POST.get('up.x'):
            if game_manager.selected > 1:
                game_manager.selected -= 1
        elif request.POST.get('down.x'):
            if game_manager.selected < 3:
                game_manager.selected += 1

    if game_manager.isGameLoaded:
        a_purpose = 'start game'
    context = {
        'selected_slot': game_manager.selected,
        'slot_a_status': save_manager.slot_a_status,
        'slot_b_status': save_manager.slot_b_status,
        'slot_c_status': save_manager.slot_c_status,
        'a_purpose': a_purpose
    }
    return render(request, 'moviemon/load.html', context)


def save(request):
    save_manager.update_files
    if request.method == "POST":
        if request.POST.get('A'):
            data = game_manager.dump()
            slot = None
            if game_manager.selected == 1:
                slot = 'a'
            elif game_manager.selected == 2:
                slot = 'b'
            elif game_manager.selected == 3:
                slot = 'c'
            save_manager.save(
                slot,
                len(game_manager.captured_moviemons),
                len(game_manager.captured_moviemons) + len(game_manager.film_ids),
                data
            )
        elif request.POST.get('B'):
            game_manager.selected = 1
            return redirect('/options')
        elif request.POST.get('up.x'):
            if game_manager.selected > 1:
                game_manager.selected -= 1
        elif request.POST.get('down.x'):
            if game_manager.selected < 3:
                game_manager.selected += 1

    context = {
        'selected_slot': game_manager.selected,
        'slot_a_status': save_manager.slot_a_status,
        'slot_b_status': save_manager.slot_b_status,
        'slot_c_status': save_manager.slot_c_status
    }
    return render(request, 'moviemon/save.html', context)
