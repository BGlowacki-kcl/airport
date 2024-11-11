from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache

from .forms import LoginForm, CreateUser

def checkIfAuthenticated(request):
    if request.user.is_authenticated:
        return redirect('Users:dashboard')


def home(request):
    checkIfAuthenticated(request)
    return render(request, "Authentication/index.html")

@never_cache
def login(request):
    checkIfAuthenticated(request)
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("Users:dashboard")
    context = {'form': form}
    return render(request,'Authentication/login.html', context=context)


def register(request):
    checkIfAuthenticated(request)
    form = CreateUser()
    if request.method == "POST":
        form = CreateUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect("Authentication:login")
    context = {'form':form}
    return render(request, 'Authentication/register.html', context=context)

def about(request):
    checkIfAuthenticated(request)
    return render(request, "Authentication/about.html") 

def user_logout(request):
    auth.logout(request)
    return render(request, "Authentication/logout.html")

# To be done
def handler404(request, exception=None):
    print("DONE")
    render(request, "Authentication/404.html", status=404)