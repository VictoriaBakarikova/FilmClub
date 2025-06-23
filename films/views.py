from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django import shortcuts
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests

from .forms import SignUpForm, LoginForm
from .models import Film, Comment, CommentLike, MovieFolder, Tag


# Create your views here.
def index(request):
    return HttpResponse("Hello")

@login_required
def home(request):
    all_films = Film.objects.order_by('-updated_at')
    page_number = request.GET.get('page', 1)

    paginator = Paginator(all_films, PAGE_SIZE)
    page = paginator.page(page_number)

    return shortcuts.render(
        request,
    "home.html",
        {
            "films": all_films[:10],
        }
    )

def increase_views(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    film.views += 1
    film.save()
    return shortcuts.render(
        request,
        "home.html",
        {"film": film
         }
    )

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect("home")
        else:
            print(f"error: {form.errors}")
            return shortcuts.render(
                request,
                "registration/signup.html",
                {"form": form
                 }
            )
    return shortcuts.render(
        request,
        "registration/signup.html",
        {"form": SignUpForm()
         }
    )

class LoginView(auth_views.LoginView):
    next_page = "/films/home"
    form_class = LoginForm

@csrf_exempt
def google_auth(request):
    token = request.POST.get("credential")

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        messages.error(request, "Try again")
        return shortcuts.render(
            request,
            "registration/login.html",
        )
    user = User.objects.acreate_user(
        username=user_data.get("username"),
        email=user_data.get("email"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
    )
    user.save()

    return shortcuts.redirect("/films/home")

class LogoutView(auth_views.LogoutView):
    next_page = "/films"

@login_required
def create_movie_folder(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if request.method == "POST":
        movie_folder = MovieFolder.objects.create(user=request.user, film=film)
        movie_folder.save()
        messages.success(request, f"You're are successfully added a '{film.title}' in your folder!")
    return redirect("film_details", film_id=film_id)


@login_required
def film_details(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    movie_folders = MovieFolder.objects.filter(user=request.user, film=film).first()
    return shortcuts.render(
        request,
        "film_details.html",
        {"film": film,
         "movie_folders": movie_folders,
         }
    )

SEARCH_RESULT_LIMIT = 5
PAGE_SIZE = 10
TAGS_LIMIT = 10


def search_films(request):
    query = request.GET.get("q")
    result = []
    if query:
        result = Film.objects.filter(Q(title__icontains=query))[:SEARCH_RESULT_LIMIT]
    return shortcuts.render(
        request,
        "components/search_results.html",
        {"result": result
         }
    )


@login_required
def my_films(request):
    tags = (
        Tag.objects
        .annotate(film_count=Count("films"))
        .order_by("-film_count")
        [: TAGS_LIMIT]
    )

    return shortcuts.render(
        request,
        "films/all_films.html",
        {
            "tags": tags,
            "my_films": True
        }
    )

def my_films_page(request):
    page_number = request.GET.get("page", 1)
    tag_ids = request.GET.getlist("tags[]")
    films_q = Film.objects.prefetch_related("tags")
    films_q = films_q.watching_movies(user=request.user).prefetch_related("tags")
    if tag_ids:
        films_q = films_q.filter(tags__id__in=tag_ids).distinct()

    paginator = Paginator(films_q, PAGE_SIZE)
    page = paginator.get_page(page_number)

    return shortcuts.render(
        request,
        "films/partials/films_list.html",
        {
            "films": page,
            "selected_tags": tag_ids,
        }
    )

def all_films(request):
    tags = (
        Tag.objects
        .annotate(film_count=Count("films"))
        .order_by("-film_count")
        [:TAGS_LIMIT]
    )

    return shortcuts.render(
        request,
        "films/all_films.html",
        {
            "tags": tags,
            "my_films": False
         }
    )

def all_films_page(request):
    page_number = request.GET.get("page", 1)
    tag_ids = request.GET.getlist("tags[]")

    films_q = Film.objects.prefetch_related("tags")


    films_q = films_q.with_movie_folders(user=request.user).prefetch_related("tags")
    if tag_ids:
        films_q = films_q.filter(tags__id__in=tag_ids).distinct()

    paginator = Paginator(films_q, PAGE_SIZE)
    page = paginator.get_page(page_number)

    return shortcuts.render(
        request,
        "films/partials/films_list.html",
        {
            "films": page,
            "selected_tags": tag_ids,
        }
    )

def add_comment(request, film_id):
    if request.method != "POST" or not request.user.is_authenticated:
        return HttpResponseBadRequest()

    film = get_object_or_404(Film, id=film_id)
    content = request.POST.get("content", "").strip()

    if not content:
        return HttpResponseBadRequest("Empty comment.")

    Comment.objects.create(film=film, user=request.user, content=content)

    comments = film.comments.order_by("-created_at")
    return render(request,
        "films/partials/comments_list.html",
            {"comments": comments
             }
    )

@login_required
def toggle_comment_like(request, comment_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest()

    comment = shortcuts.get_object_or_404(Comment, id=comment_id)
    try:
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment
        )
    except IntegrityError:
        created = False
        like = CommentLike.objects.filters(user=request.user, comment=comment).first()

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return shortcuts.render(
        request,
        "films/partials/like_button.html",
        {"comment": comment,
         "user": request.user,
         "liked": liked
         }
    )

