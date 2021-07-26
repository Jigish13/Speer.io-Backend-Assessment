import requests
import urllib.parse

import json

def lookup(symbol):
    """Look up quote for the stock symbol."""

    # Contact API
    try:
        api_key = 'pk_b6325ccbf1ff4cad8d7ba10082b31cd1';
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parsing API response  
    # and Getting stock information such as Stock's Name, Price & Symbol
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"].upper()
        }
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"