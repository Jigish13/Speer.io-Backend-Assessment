from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm, QuoteForm, BuyForm, AddBalanceForm
from .forms import CreateUserForm

from .helpers import lookup, usd
from .models import Cash, Purchase
from django.db.models import Sum

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


@login_required(login_url='login')
def sell(request):
    """Sell shares of stock"""

    if request.method == "POST":
        stock_symbol = request.POST.get("symbol")
        total_shares = request.POST.get("shares")

        # Ensure quote symbol was submitted
        if not stock_symbol:
            return render(request, "finance/sell.html", {
                    "message": "Must Provide Symbol !!"
                })

        # Ensure total no of shares was submitted
        if not total_shares:
            return render(request, "finance/sell.html", {
                    "message": "Missing Shares !!"
                })

        # Ensure total no of shares is a number
        if not total_shares.isnumeric():
            return render(request, "finance/sell.html", {
                    "message": "Invalid Input !!"
                })

        # Ensure total no of shares is not less than 1 
        if int(total_shares) < 1:
            return render(request, "finance/sell.html", {
                    "message": "Invalid Input !!"
                })

        # Grouping all the purchases done by user for given stock as per the total number of shares
        purchases = request.user.purchases.all()
        grouped_purchases = purchases.filter(stock=stock_symbol).annotate(total_shares=Sum('shares'))

        total_shares = int(total_shares)

        # Ensure user has the given stock
        if len(grouped_purchases) == 0:
            return render(request, "finance/sell.html", {
                    "message": "You don't have this stock !!"
                })

        # Ensure user has enough shares for the given stock to sell
        if total_shares > grouped_purchases[0].total_shares:
            return render(request, "finance/sell.html", {
                    "message": "Too many shares !!"
                })

        # Lookup for stock & know its current val and then sell it
        stock_data = lookup(stock_symbol)

        # Update shares column in purchase table
        transaction = Purchase(my_user=request.user, stock=stock_symbol, shares=-total_shares, price=stock_data["price"])
        transaction.save()

        # Update in_hand_money for cash table for the given user
        request.user.cash.in_hand_money += stock_data["price"]*total_shares
        request.user.cash.save()

        messages.success(request, str(total_shares) + " shares of " + stock_symbol + " was sold !!")
        return HttpResponseRedirect(reverse("index"))
    else:
        # Allowing users to see all their purchases so that they can make informed decision about selling
        purchases = request.user.purchases.all()
        stocks = set()
        for purchase in purchases:
            stock = purchase.stock
            stocks.add(stock)
        return render(request, "finance/sell.html", {
            "stocks": stocks
        })


# Homepage for users to see their portfolio(index.html)
# It will display user's total cash in hand, list of all the purchases done and its total cost
@login_required(login_url='login')
def index(request):
    cash = request.user.cash.in_hand_money
    
    # SQL Query to be executed:
    # SELECT stock, SUM(shares) FROM purchase WHERE id = user_id GROUP BY stock ORDER BY stock
    purchases = request.user.purchases.all()
    grouped_purchases = purchases.values('stock').annotate(total_shares=Sum('shares')).order_by('stock')

    total = cash
    # Modifying list of purchases and adding new key-values to each purchase obj
    for purchase in grouped_purchases:
        stock_data = lookup(purchase["stock"])
        purchase["stock"] = stock_data["symbol"]
        purchase["price"] = usd(stock_data["price"])
        purchase["name"] = stock_data["name"]
        purchase["sum"] = usd(purchase["total_shares"] * stock_data["price"])
        total = float(total) + float(purchase["total_shares"] * stock_data["price"])

    return render(request, "finance/index.html", {
        "total": usd(total),
        "cash": usd(cash),
        "purchases": grouped_purchases
    })



@login_required(login_url='login')
def add_balance(request):
    """Add Balance to user's wallet"""
    if request.method == "POST":
        form = AddBalanceForm(request.POST)
        if form.is_valid():

            # Retreive the total amount of balance user wanted to add
            add_balance = int(form.cleaned_data["add_balance"])
            
            # Ensure user has entered valid amount to add balance
            if add_balance < 1:
                return render(request, "finance/addBalance.html", {
                    "form": form,
                    "message": "Invalid amount entered !!"
                })

            # Update in_hand_money for cash table for the given user and add balance 
            request.user.cash.in_hand_money += add_balance
            request.user.cash.save()

            messages.success(request, str(add_balance) + " balance was added to your wallet !!")
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "finance/addBalance.html")
