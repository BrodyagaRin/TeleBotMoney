import sys
import telebot
from TeleBotextensions import APIException, CurrencyConverter
from TeleBotconfig import TOKEN, CURRENCY_MAP
import traceback

bot = telebot.TeleBot(TOKEN)


user_states = {}


STATE_WAITING_FOR_NAME = "waiting_for_name"
STATE_READY_FOR_CONVERSION = "ready_for_conversion"

unsupported_currencies = ["yen", "pound", "franc"]


@bot.message_handler(commands=['start', 'help'])
def welcome(message: telebot.types.Message):
    text = (
        "Hello! I can help you find out the current exchange rate.\n"
        "Please enter your name, so Bot can help you:"
    )

    user_states[message.chat.id] = STATE_WAITING_FOR_NAME
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def available_currencies(message: telebot.types.Message):
    text = "Available currencies:\n" + '\n'.join(f"- {key.capitalize()}" for key in CURRENCY_MAP.keys())
    text += "\nCurrently unavailable currencies (coming soon):\n- Yen\n- Pound\n- Franc"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == STATE_WAITING_FOR_NAME)
def ask_name(message: telebot.types.Message):
    user_name = message.text
    welcome_text = (
        f"Nice to meet you, {user_name}!\n"
        "To get the exchange rate, use the format:\n"
        "<Currency 1> <Currency 2> <Amount>\n"
        "For example: Dollar Ruble 100\n"
        "To see available currencies, type /values."
    )

    user_states[message.chat.id] = STATE_READY_FOR_CONVERSION
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == STATE_READY_FOR_CONVERSION)
def handle_conversion(message: telebot.types.Message):
    values = message.text.split()
    try:
        if len(values) != 3:
            raise APIException("Incorrect command format. Use: <Currency 1> <Currency 2> <Amount>.")

        base, quote, amount = values


        if base.lower() in unsupported_currencies or quote.lower() in unsupported_currencies:
            bot.send_message(message.chat.id,
                             f"Conversion for {base.capitalize()} and {quote.capitalize()} will be available in future updates.")
            return

        conversion_result = CurrencyConverter.get_price(base, quote, amount)


        bot.send_message(
            message.chat.id,
            f" {amount} {base.capitalize()} ➡️ {quote.capitalize()} = {conversion_result} {quote.upper()}. "
            f"To continue, write down another currencies:"

        )

    except APIException as e:
        bot.send_message(message.chat.id, f"Error: {e}")
    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, f"An error occurred: {e}")


bot.polling()
