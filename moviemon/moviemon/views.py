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
    if game_manager.current_page != '/':
        return redirect(game_manager.current_page)
    if request.method == "POST":
        save_manager.update_files()
        if request.POST.get('A'):
            game_manager.load_default_settings()
            game_manager.current_page = '/worldmap'
            return redirect('/worldmap')
        elif request.POST.get('B'):
            game_manager.current_page = '/options/load_game'
            return redirect('/options/load_game')

    return render(request, 'moviemon/title_screen.html', {})


def worldmap(request):
    if game_manager.current_page != '/worldmap':
        return redirect(game_manager.current_page)
    if request.method == "POST":
        if request.POST.get('start'):
            game_manager.current_page = '/options'
            return redirect('/options')
        elif request.POST.get('select'):
            game_manager.current_page = '/moviedex'
            return redirect('/moviedex')
        elif game_manager.isMoviemonEncountered:
            if request.POST.get('A'):
                game_manager.isMoviemonEncountered = False
                moviemon_id = game_manager.get_random_movie()
                game_manager.current_page = '/battle/' + moviemon_id
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
    if game_manager.current_page != '/battle/' + moviemon_id:
        return redirect(game_manager.current_page)
    movie = game_manager.get_movie(moviemon_id)
    movie_poster_url = movie["Poster"]

    if request.method == "POST":
        if game_manager.isMovieballThrown:
            if game_manager.isMoviemonCatched:
                if request.POST.get('B'):
                    game_manager.isMovieballThrown = False
                    game_manager.isMoviemonCatched = False
                    game_manager.current_page = '/worldmap'
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
                game_manager.current_page = '/worldmap'
                return redirect('/worldmap')

    context = {
        "moviemon_img_url": movie_poster_url,
        "player_strength": game_manager.get_strength(),
        "moviemon_strength": round(float(movie["imdbRating"])),
        "movieballs": game_manager.player_movieballs,
        'winrate': game_manager.calculate_chance(moviemon_id),
        "isMovieballThrown": game_manager.isMovieballThrown,
        "isMoviemonCatched": game_manager.isMoviemonCatched
    }
    return render(request, 'moviemon/battle.html', context)


def moviedex(request):
    if game_manager.current_page != '/moviedex':
        return redirect(game_manager.current_page)

    if request.POST.get('select'):
        game_manager.current_page = '/worldmap'
        return redirect('/worldmap')

    moviemons_num = len(game_manager.captured_moviemons)
    if moviemons_num == 0:
        return render(request, 'moviemon/moviedex.html', {"moviedex": []})

    select = game_manager.moviemon_selected
    if request.POST.get('A'):
        moviemon_id = game_manager.captured_moviemons[select]['imdbID']
        game_manager.current_page = f'/moviedex/{moviemon_id}'
        return redirect(f'/moviedex/{moviemon_id}')
    elif request.POST.get('right.x'):
        game_manager.moviemon_selected = select + 1 if select < moviemons_num - 1 else select
    elif request.POST.get('left.x'):
        game_manager.moviemon_selected = select - 1 if select > 0 else select

    moviemons = [(moviemon["Poster"], moviemon['imdbID'], True if i == game_manager.moviemon_selected else False)
                 for i, moviemon in enumerate(game_manager.captured_moviemons)]
    context = {"moviedex": moviemons}
    return render(request, 'moviemon/moviedex.html', context)


def detail(request, moviemon=None):
    if game_manager.current_page != '/moviedex/' + moviemon:
        return redirect(game_manager.current_page)

    if request.method == "POST":
        if request.POST.get('B'):
            game_manager.current_page = '/moviedex'
            return redirect('/moviedex')
    for a in game_manager.captured_moviemons:
        if a['imdbID'] == moviemon:
            moviemon = ({
                'Title': a['Title'],
                'Year': a['Year'],
                'Genre': a['Genre'],
                'Director': a['Director'],
                'Actors': a['Actors'],
                'Plot': a['Plot'],
                'Country': a['Country'],
                'Rating': a['imdbRating']
            }, a['Poster'])
    context = {'moviemon': moviemon}
    return render(request, 'moviemon/detail.html', context)


def options(request):
    if game_manager.current_page != '/options':
        return redirect(game_manager.current_page)

    if request.method == "POST":
        if request.POST.get('start'):
            game_manager.current_page = '/worldmap'
            return redirect('/worldmap')
        elif request.POST.get('A'):
            game_manager.current_page = '/options/save_game'
            return redirect('/options/save_game')
        elif request.POST.get('B'):
            game_manager.current_page = '/'
            return redirect('/')
    context = {}
    return render(request, 'moviemon/options.html', context)


def load(request):
    global game_manager
    if game_manager.current_page != '/options/load_game':
        return redirect(game_manager.current_page)

    save_manager.update_files()
    a_purpose = 'A - Load, B - Cancel'
    if request.method == "POST":
        if request.POST.get('A'):
            if game_manager.isGameLoaded == True:
                game_manager.isGameLoaded = False
                game_manager.current_page = '/worldmap'
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
        elif request.POST.get('B') and not game_manager.isGameLoaded:
            game_manager.selected = 1
            game_manager.current_page = '/'
            return redirect('/')
        elif request.POST.get('up.x'):
            if game_manager.selected > 1:
                game_manager.selected -= 1
        elif request.POST.get('down.x'):
            if game_manager.selected < 3:
                game_manager.selected += 1

    if game_manager.isGameLoaded:
        a_purpose = 'A - Start game'
    context = {
        'selected_slot': game_manager.selected,
        'slot_a_status': save_manager.slot_a_status,
        'slot_b_status': save_manager.slot_b_status,
        'slot_c_status': save_manager.slot_c_status,
        'a_purpose': a_purpose
    }
    return render(request, 'moviemon/load.html', context)


def save(request):
    if game_manager.current_page != '/options/save_game':
        return redirect(game_manager.current_page)

    save_manager.update_files()
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
            game_manager.current_page = '/options'
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
