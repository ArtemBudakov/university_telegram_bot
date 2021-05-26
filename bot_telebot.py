import datetime

import telebot
import requests
from configuration import token_telegram, token_weatherstack
bot = telebot.TeleBot(token_telegram, parse_mode=None)


def get_weather_request(city):
    params = {"access_key": token_weatherstack, "query": city, "language": 'ru'}
    try:
        api_result = requests.get('http://api.weatherstack.com/current', params)
        api_response = api_result.json()
        # api_response = f"temperature in {city} - {api_response['current']['temperature']} degrees"
        current_temperature = api_response['current']['temperature']
        print(api_response)
        api_response = f"В городе {city} сейчас {current_temperature} градусов." \
                       f"сегодня {datetime.date.today()}"
    except:
        print('error')
        api_response = "Что-то пошло не так. Проверьте - правильно ли написано "\
                       "название города и попробуйте снова"
    finally:
        return api_response


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет. У меня можно узнать погоду\n"
                          "Чтобы узнать погоду - напишите 'погода'")


@bot.message_handler(commands=['weather', 'погода'])
def send_weather(message):
    bot.reply_to(message, "Напишите название города для которого вы хотите узнать погоду.")


@bot.message_handler()
def send_current_weather(message):
    print(message.from_user.id)
    current_weather = get_weather_request(message.text)
    bot.reply_to(message, current_weather)


# bot.polling()
# bot.remove_webhook()

if __name__ == '__main__':
    get_weather_request('moscow')
