from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('worldmap', views.worldmap, name='worldmap'),
    path('moviedex', views.moviedex, name='moviedex'),
    path('detail', views.detail, name='detail'),
    path('options', views.options, name='options'),
    path('battle', views.battle, name='battle'),
    path('options/load_game', views.load, name='load'),
    path('options/save_game', views.save, name='save')
]
