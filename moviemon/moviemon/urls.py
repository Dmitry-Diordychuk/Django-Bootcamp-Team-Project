from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('worldmap', views.worldmap, name='worldmap'),
    path('moviedex', views.moviedex, name='moviedex'),
    path('moviedex/<str:moviemon>', views.detail, name='detail'),
    path('options', views.options, name='options'),
    path('battle/<str:moviemon_id>/', views.battle, name='battle'),
    path('options/load_game', views.load, name='load'),
    path('options/save_game', views.save, name='save'),
    # path('moviemon/detail', views.detail, name='detail')
]
