import telebot
import requests
from telebot import types
from configuration import token_telegram, token_openweather
bot = telebot.TeleBot(token_telegram, parse_mode=None)  # указываем токен телеграм бота для корректной
                                                        # работы библиотеки telebot

city_global = "saint petersburg"  # глобальная переменная для указания и хранения города.


# функция для получения погоды с openweather, с указанием города и количества дней. по умолчанию - два дня
def get_weather_from_openweather(city, days=2):
    # параметры для формирования запроса в вид http://api.openweathermap.org/data/2.5/forecast?appid={TOKEN}&q={CITY}
    params = {"appid": token_openweather, "q": city}

    # попытайся
    try:
        # формирование запроса и отправка его методом GET
        api_result = requests.get('http://api.openweathermap.org/data/2.5/forecast', params)
        # берём ответ от API и преобразуем его в json (dict для python)
        api_response = api_result.json()

        # переменная для всех дней
        every_days: str = ""
        # для каждого блока данных в списке делаем то, что ниже
        for block_of_data in api_response['list']:
            # если 0 дней, то выходим из цикла
            if days == 0:
                break
            # получаем дату и время из dt_txt
            time = block_of_data['dt_txt']
            # убираем дату и оставляем только время, которое должно быть
            # равно 12:00:00 (апи даёт информацию через каждые 3 часа)
            if time[11:] == "12:00:00":
                # берём полную дату из блока
                data = block_of_data['dt_txt']
                # получаем температуру из ['main']['temp'] в Кельвинах, форматируем её, преобразуем в int, затем
                # получаем Цельсий, после чего преобразуем в строку
                temperature = str((int('{0:+3.0f}'.format(block_of_data['main']['temp']))) - 273.15)
                # короткое описание погоды, согласно протоколу getweatherAPI
                # description = i['weather'][0]['description']
                # получаем скорость ветра из ['wind']['speed']
                wind = block_of_data['wind']['speed']
                # форматируем данные и собираем блок для удобного вывода, убирая время (оставляем дату) и убираем
                # лишние знаки в температуре
                one_block = f'{data[:10]}, темература {temperature[:5]} ℃, скорость ветра {wind}\n'
                # добавляем блок в переменную, которая содержит все необходимые блоки
                every_days += str(one_block)
                print(one_block)
                # вычитаем день, чтобы получить погоду только на нужный период
                days -= 1
        # кладём в переменную все блоки чтобы вернуть return'ом из функции
        api_response = every_days
    # в случае возникновения исключения(ошибки) назвать её как 'e' и сделать следующее
    except Exception as e:
        print('error')
        # вывести ошибку из переменной 'e'
        print("Exception (forecast):", e)
        api_response = "Что-то пошло не так. Проверьте - правильно ли написано " \
                       "название города и попробуйте снова"
    # после try или except выполнить
    finally:
        # вернуть api_response
        return api_response


# декоратор для telebot. обозначаем комадны для реакции бота на "/start" и так далее
@bot.message_handler(commands=['start', 'help', 'старт', 'помощь'])
# функция отправить приветствие (и ответ на помощь). получаем сообщение от пользователя
def send_welcome_or_help(message):
    # дублирует то, что написал пользователь и выводит сообщение
    bot.reply_to(message, "Привет. У меня можно узнать погоду\n"
                          "Напишите название города для которого вы хотите узнать погоду.\n"
                          "Затем напишите 'weather' или 'погода' чтобы выбрать количество дней (максимум 5).")


# декоратор для telebot. обозначаем комадны для реакции бота на "/weather" и так далее
@bot.message_handler(commands=['weather', 'погода'])
# функция предлагает выбрать кол-во дней в виде кнопок. получает сообщение от пользователя
def send_buttons(message):
    # задаём переменную для всех кнопок и обозначаем тип кнопок
    markup_inline = types.InlineKeyboardMarkup()
    # формируем элемент и его параметны для всех кнопок
    item_one = types.InlineKeyboardButton(text='1 день', callback_data='1 day')
    item_two = types.InlineKeyboardButton(text='2 дня', callback_data='2 days')
    item_three = types.InlineKeyboardButton(text='3 дня', callback_data='3 days')
    item_four = types.InlineKeyboardButton(text='4 дня', callback_data='4 days')
    item_five = types.InlineKeyboardButton(text='5 дней', callback_data='5 days')
    # добавляем все кнопки в переменную
    markup_inline.add(item_one, item_two, item_three, item_four, item_five)
    # отправляем сообщение пользователю, учитывая chat.id
    bot.send_message(message.chat.id, 'Погоду на сколько дней показать?', reply_markup=markup_inline)


# декоратор для telebot для обработки callback, который исполняется после нажатия пользователем на кнопку
@bot.callback_query_handler(func=lambda call: True)
# функция задаёт кол-во дней, получает погоду погоду с апи и отправляет её пользователю
def send_weather(call):
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

    # говорим, что мы используем глобальную переменную
    global city_global
    # получаем текущую погоду и кладём её в переменную current_weather
    current_weather = get_weather_from_openweather(city_global, days)
    # отправляем данные пользователю
    bot.send_message(call.message.chat.id, f"Погода в городе {city_global}:\n"
                                           f"{current_weather}")


# декоратор для telebot для обработки обычных сообщений от пользователя
@bot.message_handler()
def set_city(message):
    # говорим, что мы используем глобальную переменную
    global city_global
    # в глобальную переменную кладём требуемый город, который получаем от пользователя. (Если город неверно написан, то
    # при запросе для получаения погоды с api будем получать ошибку
    city_global = message.text
    print(f"city is {city_global}")
    # отправляем ответ пользователю
    bot.reply_to(message, f"Ваш город - {city_global}")


# используем для запуска webhook'а
bot.polling()
