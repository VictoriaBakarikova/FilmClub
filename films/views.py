from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import SignUpForm, LoginForm
from .models import Film



# Create your views here.
def index(request):
    return HttpResponse("Hello")

@login_required
def home(request):
    recent_films = Film.objects.order_by("-created_at")[:10]
    context = {"recent_films": recent_films}
    return render(request, "home.html", context)

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
    next_page = "/films/home"
    form_class = LoginForm

class LogoutView(auth_views.LogoutView):
    next_page = "/films"
