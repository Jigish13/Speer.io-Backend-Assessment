from StockMarket.finance.views import add_balance
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class QuoteForm(forms.Form):
    symbol = forms.CharField(label="Symbol ", max_length=5)
    error_css_class = 'error'
    required_css_class = 'bold'

class BuyForm(forms.Form):
    symbol = forms.CharField(label="Symbol", max_length=5)
    shares = forms.IntegerField(label="Shares", min_value=1)
    error_css_class = 'error'
    required_css_class = 'bold'

class AddBalanceForm(forms.Form):
    add_balance = forms.IntegerField(label="Add Balance", min_value=1)
    error_css_class = 'error'
    required_css_class = 'bold'