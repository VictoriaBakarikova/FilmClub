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
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests

from .forms import SignUpForm, LoginForm
from .models import Film, MovieFolder, Tag


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
            "films": page,
            "has_next": page.has_next(),
            "next_page": (
                page.next_page_number()
                if page.has_next()
                else None,
            )
        }
    )





    # found_films = Film.objects.order_by('-created_at')[:5]
    # popular_films = Film.objects.order_by('-views')[:5]
    # recent_films = Film.objects.order_by("-created_at")[:10]
    # context = {
    #     "found_films" : found_films,
    #     "popular_films": popular_films,
    #     "recent_films": recent_films,
    # }
    # return render(request,
    #               "home.html",
    #               context)

def increase_views(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    film.views += 1
    film.save()
    return shortcuts.render(
        request,
        "home.html",
        {"film": film})

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
    return shortcuts.render(
        request,
        "film_details.html",
        {"film": film
         }
    )

SEARCH_RESULT_LIMIT = 5

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

# def film_details(request, film_id):
#     def film_details(request, film_id):
#         film = get_object_or_404(Film, id=film_id)
#         movie_folder = MovieFolder.objects.filter(film=request.user, id=film.id).first()
#         return shortcuts.render(
#             request,
#             "film_details.html",
#             {
#                 "film": film,
#                 "movie_folder": movie_folder,
#             }
#         )

PAGE_SIZE = 10

@login_required
def my_films(request):
    movie_folder = (
        MovieFolder.objects
        .filter(user=request.user)
        .select_related("film")
    )

    page_number = request.GET.get("page", 1)
    paginator = Paginator(movie_folder, PAGE_SIZE)
    page = paginator.get_page(page_number)

    if request.headers.get('HX-Request') == 'true':
        return shortcuts.render(
            request,
            "films_list_page.html",
            {
                "movie_folders": page,
            }
        )

    popular_films = Film.objects.order_by("-views")[:SEARCH_RESULT_LIMIT]
    return shortcuts.render(
        request,
        "my_films.html",
        {
            "movie_folders": page,
            "popular_films": popular_films,
            "has_next":page.has_next(),
            "next_page":(
                page.next_page_number()
                if page.has_next()
                else None
            )
        }
    )

TAGS_LIMIT = 10

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
         }
    )

def all_films_page(request):
    page_number = request.GET.get("page", 1)
    tag_ids = request.GET.getlist("tags[]")

    films_q = Film.objects.prefetch_related("tags")
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


