import requests
import json
from TeleBotconfig import CURRENCY_MAP


class APIException(Exception):
    pass


class CurrencyConverter:
    @staticmethod
    def get_price(base, quote, amount):
        try:
            base_currency = CURRENCY_MAP[base.lower()]
        except KeyError:
            raise APIException(f"Currency '{base}' not found. Please try another.")

        try:
            quote_currency = CURRENCY_MAP[quote.lower()]
        except KeyError:
            raise APIException(f"Currency '{quote}' not found. Please try another.")

        if base_currency == quote_currency:
            raise APIException(f"Cannot convert the same currency: {base}!")

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f"Invalid amount: '{amount}'. Please enter a number.")

        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency}")
        rates = response.json()['rates']

        if quote_currency not in rates:
            raise APIException(f"Failed to get the rate for '{quote}'.")

        conversion_rate = rates[quote_currency]
        total = round(conversion_rate * amount, 2)
        return total  
