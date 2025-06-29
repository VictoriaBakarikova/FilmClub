from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("movie_folders/<int:film_id>/", views.MovieFolder, name="movie_folder"),
    path("films/<int:film_id>/", views.film_details, name="film_details"),
    path("films/<int:film_id>/comments", views.add_comment, name="add_comment"),
    path("comments/<int:comment_id>/like", views.toggle_comment_like, name="toggle_comment_like"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("films/my_films/", views.my_films, name="my_films"),
    path("films/<int:film_id>/change_status/", views.change_status, name="change_status"),
    path("films/<int:film_id>/add_to_folder/", views.add_to_folder, name="add_to_folder"),
    path("films/<int:film_id>/remove_from_folder/", views.remove_from_folder, name="remove_from_folder"),
    path("films/<int:film_id>/status_badge_partial/",views.status_badge_partial,name="status_badge_partial"),
    path("films/<int:film_id>/rate/", views.rate_film, name="rate_film"),
    path("my_films/page", views.my_films_page, name="my_films_page"),
    path("films/all_films/", views.all_films, name="all_films"),
    path("all_films/page", views.all_films_page, name="all_films_page"),
    path("films/search/", views.search_films, name="search_films"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/login/", views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("auth/logout/", views.goodbye_logout, name="logout"),
    path("google-auth/", views.google_auth, name="google-auth"),
    path("profile/", views.profile, name="profile"),
    path("add-film/", views.add_film, name="add_film"),

]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
