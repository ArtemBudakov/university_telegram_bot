import requests
from configuration import token_telegram, token_weatherstack
from flask import Flask, request
app = Flask(__name__)


def send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{token_telegram}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def get_weather(city):
    params = {"access_key": token_weatherstack, "query": city, "forecast days": 3}
    api_result = requests.get('http://api.weatherstack.com/current', params)
    api_response = api_result.json()
    print(api_response)
    return f"temperature in {city} - {api_response['current']['temperature']} degrees"


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        print(request.json)
        chat_id = request.json["message"]["chat"]["id"]
        city = request.json["message"]["text"]
        if city in ['london', 'moscow', 'saint-petersburg', 'abu-dabi']:
            send_message(chat_id, get_weather(city))
        else:
            text = "sorry, but I have not information about this city"
            send_message(chat_id, text)
    return {"ok": True}
