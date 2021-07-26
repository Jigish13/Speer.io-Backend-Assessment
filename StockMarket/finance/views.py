from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

# Create your views here.

# Allowing users to login
def login_view(request):
    # If user is authenticated then allow user to see their portfolio 
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication is successful
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.info(request, "Username OR password is incorrect")
                return render(request, "finance/login.html")
        else:
            return render(request, "finance/login.html")

# Allowing users to logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfuly.")
    return redirect("login")

# Allowing users to Sign Up
def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:        
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                # Attempt to create new user
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, "Account was created for " + username)
                
                return redirect("login")
        
        return render(request, "finance/register.html", {
            'form': form
        })
