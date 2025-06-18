from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("movie_folders/<int:film_id>/", views.MovieFolder, name="movie_folder"),
    path("films/<int:film_id>/", views.film_details, name="film_details"),
    path("films/my_films/", views.my_films, name="my_films"),
    path("films/search/", views.search_films, name="search_films"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/login/", views.login, name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
