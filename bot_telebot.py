import telebot
import requests
from telebot import types
from configuration import token_telegram, token_openweather
bot = telebot.TeleBot(token_telegram, parse_mode=None)

city_global = "saint petersburg"
clients_global = {}


def get_weather_from_openweather(city, days=2):
    params = {"appid": token_openweather, "q": city}
    try:
        api_result = requests.get('http://api.openweathermap.org/data/2.5/forecast', params)
        api_response = api_result.json()

        every_days: str = ""
        for i in api_response['list']:
            if days == 0:
                break
            time = i['dt_txt']
            if time[11:] == "12:00:00":
                data = i['dt_txt']
                temperature = str((int('{0:+3.0f}'.format(i['main']['temp']))) - 273.15)
                # description = i['weather'][0]['description']
                wind = i['wind']['speed']
                one_block = f'{data[:10]}, темература {temperature[:5]} ℃, скорость ветра {wind}\n'
                every_days += str(one_block)
                print(one_block)
                days -= 1
        api_response = every_days
    except Exception as e:
        print("Exception (forecast):", e)
        api_response = "Что-то пошло не так. Проверьте - правильно ли написано " \
                       "название города и попробуйте снова"
    finally:
        return api_response


@bot.message_handler(commands=['start', 'help', 'старт', 'помощь'])
def send_welcome(message):
    bot.reply_to(message, "Привет. У меня можно узнать погоду\n"
                          "Укажите город.\n")


@bot.message_handler(commands=['weather', 'погода'])
def start(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_one = types.InlineKeyboardButton(text='1 день', callback_data='1 day')
    item_two = types.InlineKeyboardButton(text='2 дня', callback_data='2 days')
    item_three = types.InlineKeyboardButton(text='3 дня', callback_data='3 days')
    item_four = types.InlineKeyboardButton(text='4 дня', callback_data='4 days')
    item_five = types.InlineKeyboardButton(text='5 дней', callback_data='5 days')
    markup_inline.add(item_one, item_two, item_three, item_four, item_five)
    bot.send_message(message.chat.id, 'Погоду на сколько дней показать?', reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == '1 day':
        days = 1
    elif call.data == '2 days':
        days = 2
    elif call.data == '3 days':
        days = 3
    elif call.data == '4 days':
        days = 4
    else:
        days = 5

    global city_global
    current_weather = get_weather_from_openweather(city_global, days)
    bot.send_message(call.message.chat.id, f"Погода в городе {city_global}:\n"
                                           f"{current_weather}")


@bot.message_handler()
def send_current_weather(message):

    if message.text.isdigit() and 0 < int(message.text) <= 5:
        try:
            global clients_global
            clients_global[message.chat.id]['days'] = message.text
            if clients_global[message.chat.id]["city"] == '':
                bot.send_message(chat_id=message.chat.id, text="выберите город")
            else:
                current_weather = get_weather_from_openweather(city=clients_global[message.chat.id]["city"],
                                                               days=int(clients_global[message.chat.id]["days"]))
                bot.send_message(chat_id=message.chat.id, text=current_weather)
        except KeyError:
            # global clients_global
            clients_global[message.chat.id] = {'days': message.text, 'city': ''}
            print(clients_global)
            bot.send_message(chat_id=message.chat.id, text=f"Напишите название города")

    elif len(message.text) == 1 and message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text=f"Недопустимое количество дней")

    else:
        try:
            clients_global[message.chat.id]['city'] = message.text
        except KeyError:
            clients_global[message.chat.id] = {'days': "", "city": message.text}
        current_weather = get_weather_from_openweather(clients_global[message.chat.id]['city'])
        if current_weather == "Что-то пошло не так. Проверьте - правильно ли написано " \
                              "название города и попробуйте снова":
            bot.send_message(chat_id=message.chat.id, text=current_weather)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=f"Вы выбрали город - {clients_global[message.chat.id]['city']}\n"\
                                  f"На сколько дней выдать прогноз?")

    # bot.reply_to(message, f"Ваш город - {city_global}")


bot.polling()
