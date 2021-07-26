from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm, QuoteForm, BuyForm
from .forms import CreateUserForm

from .helpers import lookup, usd
from .models import Cash, Purchase

from django.contrib.auth.decorators import login_required
from django.urls import reverse

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

@login_required(login_url='login')
def quote(request):
    """Get stock information and its live rates"""
    if request.method == "POST":

        # using Django Form to create stock quote form
        form = QuoteForm(request.POST)

        # Here we are validating the form on the server side
        if form.is_valid():
            # Contacting IEX cloud API to retrieve stock information
            stock_data = lookup(form.cleaned_data["symbol"])

            # Ensure it is valid symbol
            if not stock_data:
                return render(request, "finance/quote.html", {
                    "form": form,
                    "message": "Invalid Symbol !!"
                })

            # Valid stock information will be returned and displayed by quoted.html page
            return render(request, "finance/quoted.html", {
                "name": stock_data["name"], 
                "symbol": stock_data["symbol"], 
                "price": usd(stock_data["price"]),
            })

    else:
        return render(request, "finance/quote.html", {
            "form": QuoteForm()
        })

@login_required(login_url='login')
def buy(request):
    """Buy shares of stock"""
    if request.method == "POST":
        form = BuyForm(request.POST)

        if form.is_valid():

            stock_symbol = form.cleaned_data["symbol"]
            total_shares = form.cleaned_data["shares"]
            
            # Calling API to get stock information
            stock_data = lookup(stock_symbol)

            # Ensure it is valid symbol
            if not stock_data:
                return render(request, "finance/buy.html", {
                    "form": form,
                    "message": "Invalid Symbol !!"
                })

            # Ensure user has enough cash to purchase shares
            stock_price = stock_data["price"]
            total_cost = float(stock_price) * int(total_shares)

            if float(request.user.cash.in_hand_money) < total_cost:
                return render(request, "finance/buy.html", {
                    "form": form,
                    "message": "Sorry you don't have enough cash !!"
                })

            # Commit a transaction for the user and insert data in Purchase table/model
            transaction = Purchase(my_user=request.user, stock=stock_symbol, shares=total_shares, price=stock_price)
            transaction.save()

            # Update in_hand_money for cash table for the given user
            request.user.cash.in_hand_money -= total_cost
            request.user.cash.save()

            messages.success(request, str(total_shares) + " shares of " + stock_symbol + " was bought !!")
            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "finance/buy.html", {
            "form": BuyForm()
        })
