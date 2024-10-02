import sys

try:
    import telebot
    from extensions import APIException, CurrencyConverter
    from config import TOKEN, CURRENCY_MAP
    import traceback
except ImportError as e:
    print(f"Error: Missing library {e.name}. Please install the required libraries using the command: \n\npip install pyTelegramBotAPI requests")
    sys.exit(1)


bot = telebot.TeleBot(TOKEN)

CURRENCY_MAP = {
    'dollar': 'USD',
    'euro': 'EUR',
    'ruble': 'RUB'
}


@bot.message_handler(commands=['start', 'help'])
def welcome(message: telebot.types.Message):
    text = (
        "Hello! I can help you find out the current exchange rate.\n"
        "Please enter your name so we can continue the conversation."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
def ask_name(message: telebot.types.Message):
    user_name = message.text
    welcome_text = (
        f"Nice to meet you, {user_name}!\n"
        "To get the exchange rate, use the format:\n"
        "<currency 1> <currency 2> <amount>\n"
        "For example: dollar ruble 100\n"
        "To see available currencies, type /values."
    )
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['values'])
def available_currencies(message: telebot.types.Message):
    text = "Available currencies:\n" + '\n'.join(CURRENCY_MAP.keys())
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def handle_conversion(message: telebot.types.Message):
    values = message.text.split()
    try:
        if len(values) != 3:
            raise APIException("Incorrect command format. Use: <currency 1> <currency 2> <amount>")

        base, quote, amount = values
        conversion_result = CurrencyConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f"Error: {e}")
    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, f"An error occurred: {e}")
    else:
        bot.send_message(message.chat.id, conversion_result)

bot.polling()
