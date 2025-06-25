
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django import shortcuts
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.db.models import Avg
from itertools import zip_longest

from .forms import SignUpForm, LoginForm
from .models import Film, Comment, CommentLike, MovieFolder, Tag
from films import utils


# Create your views here.
def index(request):
    return HttpResponse("Hello")



# def group_in_batches(lst, size):
#     args = [iter(lst)] * size
#     return zip_longest(*args, fillvalue=None)


def home(request):
    top_films = Film.objects.annotate(
        avg_rating=Avg("folder__rating")
    ).filter(avg_rating__isnull=False).order_by("-avg_rating")[:10]

    tags = Tag.objects.annotate(
        film_count=Count("films")).order_by("-film_count")

    all_films = Film.objects.all()
    recent_comments = Comment.objects.select_related("film", "user").order_by("-created_at")[:10]

    return render(request, "home.html", {
        "top_films": top_films,
        "recent_comments": recent_comments,
        "all_films": all_films,
        "tags": tags,
    })


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
    film = get_object_or_404(Film, pk=film_id)
    rating_range = range(1, 6)

    user_folder = MovieFolder.objects.filter(user=request.user, film=film).first()
    return shortcuts.render(
        request,
        "film_details.html",
        {"film": film,
         "user_folder": user_folder,
         "rating_range": rating_range,
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


from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest

@login_required
@require_POST
def change_status(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    new_status = request.POST.get("status")

    if new_status not in dict(MovieFolder.STATUS_CHOICES).keys():
        return HttpResponseBadRequest("Invalid status")

    folder, _ = MovieFolder.objects.get_or_create(user=request.user, film=film)
    folder.status = new_status
    folder.save()

    return render(
        request,
        "films/partials/status_badge.html",
        {
        "user_folder": folder,
        "film": film
    })


@login_required
def status_badge_partial(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    user_folder = MovieFolder.objects.filter(user=request.user, film=film).first()
    return render(request, "films/partials/status_badge.html", {
        "film": film,
        "user_folder": user_folder
    })


@login_required
@require_POST
def add_to_folder(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    status = request.POST.get("status", "want-to-watch")

    folder, created = MovieFolder.objects.get_or_create(
        user=request.user,
        film=film,
        defaults={"status": status}
    )

    return render(request, "films/partials/folder_button.html", {
        "film": film,
        "user_folder": folder,
    })

@login_required
@require_POST
def remove_from_folder(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    MovieFolder.objects.filter(user=request.user, film=film).delete()

    return render(request, "films/partials/folder_button.html", {
        "film": film,
        "user_folder": None,
    })

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



@login_required
@require_POST
def add_comment(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    content = request.POST.get("content", "").strip()

    if not content:
        return HttpResponseBadRequest("Empty comment.")

    Comment.objects.create(
        user=request.user,
        film=film,
        content=content,
    )

    return shortcuts.render(
        request,
        "films_details",
        {"film_id":film_id,
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

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return HttpResponseForbidden("You can delete only your own comments.")

    comment.delete()
    messages.success(request, "Комментарий удалён.")
    return redirect("film_details", film_id=comment.film.id)


@login_required
def rate_film(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    movie_folder = MovieFolder.objects.filter(user=request.user, film=film).first()

    if movie_folder is None or movie_folder.status != "watch":
        return HttpResponseBadRequest("You can rate only films you've watched.")

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        is_new = movie_folder.rating is None
        movie_folder.rating = rating
        movie_folder.save()

        if is_new and rating:
            film.rating_count += 1

        film.average_rating = MovieFolder.objects.filter(
            film=film, rating__isnull=False
        ).aggregate(avg=Avg("rating"))["avg"]
        film.save()

    return render(
        request,
        "films/partials/rating.html",
        {
            "film": film,
            "movie_folder": movie_folder,
            "rating_range": range(1, 6),
        }
    )

# def top_rated_films(request):
#     films = Film.objects.annotate(
#         avg_rating=Avg("rating__value"),
#     ).order_by("-avg_rating")[:10]
#
#     return render(
#         request,
#         "films/components/top_rated_films.html",
#         {"films": films}
#     )


