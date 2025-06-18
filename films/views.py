from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.views import shortcut
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .forms import SignUpForm, LoginForm
from .models import Film, MovieFolder


# Create your views here.
def index(request):
    return HttpResponse("Hello")

@login_required
def home(request):
    found_films = Film.objects.order_by('-created_at')[:5]
    popular_films = Film.objects.order_by('-views')[:5]
    recent_films = Film.objects.order_by("-created_at")[:10]
    context = {
        "found_films" : found_films,
        "popular_films": popular_films,
        "recent_films": recent_films,
    }
    return render(request, "home.html", context)

def increase_views(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    film.views += 1
    film.save()
    return render(request, "home.html", {"film": film})

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
            return render(request, "registration/signup.html", {"form": form})
    return render(request, "registration/signup.html", {"form": SignUpForm()})

class LoginView(auth_views.LoginView):
    form_class = LoginForm

class LogoutView(auth_views.LogoutView):
    redirect_field_name = "next"

@login_required
def film_details(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    return render(request, "film_details.html", {"film": film})

SEARCH_RESULT_LIMIT = 5

def search_films(request):
    query = request.GET.get("q")
    result = []
    if query:
        result = Film.objects.filter(Q(title__icontains=query))[:SEARCH_RESULT_LIMIT]
    return render(
        request,
        "components/search_results.html",
        {"result": result
         }
    )

def film_details(request, film_id):
    def film_details(request, film_id):
        film = get_object_or_404(Film, id=film_id)
        movie_folder = MovieFolder.objects.filter(film=request.user, id=film.id).first()
        return render(
            request,
            "film_details.html",
            {
                "film": film,
                "movie_folder": movie_folder,
            }
        )
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
        return render(
            request,
            "films_list_page.html",
            {
                "movie_folders": page,
            }
        )

    popular_films = Film.objects.order_by("-views")[:SEARCH_RESULT_LIMIT]
    return render(
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



