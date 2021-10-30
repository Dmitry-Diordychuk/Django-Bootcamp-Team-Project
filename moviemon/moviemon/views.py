from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader

import logging

from game.data_manager import DataManager

logger = logging.getLogger(__name__)
game_manager = DataManager()

# Create your views here.
def index(request):
    if request.method == "POST":
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
                return redirect('/battle')
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

        # TODO: refactoring magic method
        game_manager.check_encounter()

    context = {
        'map': game_manager.get_map(),
        'movieballs': game_manager.player_movieballs,
        'isMoviemonEncountered': game_manager.isMoviemonEncountered, # game_manager.check_encounter() change this varible
        'isMovieballFound': game_manager.isMovieballFound            # game_manager.check_encounter() change this varible
    }
    return render(request, 'moviemon/worldmap.html', context)


def battle(request):
    context = {}
    return render(request, 'moviemon/battle.html', context)


def moviedex(request):
    context = {}
    return render(request, 'moviemon/moviedex.html', context)


def detail(request):
    context = {}
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
    context = {}
    return render(request, 'moviemon/load.html', context)


def save(request):
    if request.method == "POST":
        if request.POST.get('B'):
            return redirect('/options')
    context = {}
    return render(request, 'moviemon/save.html', context)
