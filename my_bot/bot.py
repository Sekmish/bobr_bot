import telebot
from config import TOKEN, YANDEX_API_KEY
from extensions import BusSchedule, APIException
from datetime import datetime
import pytz
import requests

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    instructions = "Привет! Я бот для получения расписания автобусов.\n\n" \
                   "Для получения расписания пригородных автобусов Екатеринбург - Бобровский (ООО 'Авто-Плюс' г.Екатеринбург) используйте команду /bus_plus.\n\n" \
                    "Для получения расписания маршрута №113 Бобровский-Екатеринбург используйте команду /bus_113."
    bot.reply_to(message, instructions)
    

@bot.message_handler(commands=['bus_plus'])
def handle_bus(message):
    try:
        start_bus = "c54" # код станции Екатеринбург, Южный автовокзал
        end_bus = "c20262" # код станции Бобровский, Дом культуры
        date_bus = datetime.now().strftime("%Y-%m-%d") # текущая дата
        schedule = BusSchedule.get_bus(start_bus, end_bus, date_bus, YANDEX_API_KEY)
        response = "Расписание автобусов на {}:\n\n".format(date_bus)
        tz = pytz.timezone('Asia/Yekaterinburg')  # Часовой пояс Екатеринбурга
        current_time = datetime.now().astimezone(tz)
        for segment in schedule:
            departure_utc = datetime.strptime(segment["departure"], "%Y-%m-%dT%H:%M:%S%z")
            departure_local = departure_utc.astimezone(tz)
            arrival_utc = datetime.strptime(segment["arrival"], "%Y-%m-%dT%H:%M:%S%z")
            arrival_local = arrival_utc.astimezone(tz)
            if departure_local < current_time:
                continue  # Пропускаем рейсы, которые уже ушли
            from_station = segment["from"]["title"]
            to_station = segment["to"]["title"]
            departure_time = departure_local.strftime("%Y-%m-%d %H:%M") + " (убытие)"
            arrival_time = arrival_local.strftime("%Y-%m-%d %H:%M") + " (прибытие)"
            response += "{} - {}: {} - {}\n".format(from_station, to_station, departure_time, arrival_time)
            response += "-" * 20 + "\n"  # Полоса в качестве разделителя
        response += "Данные взяты с Яндекс.Расписание"
        bot.reply_to(message, response)
    except APIException as e:
        bot.reply_to(message, f"Ошибка: {e}")
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {e}")


@bot.message_handler(commands=['bus_113'])
def handle_bus_113(message):
    try:
        url = "https://sysert.life/wp-content/uploads/2022/10/marshruty-1.jpg"
        response = requests.get(url)
        if response.status_code == 200:
            with open("marshruty-1.jpg", "wb") as f:
                f.write(response.content)
            bot.send_photo(message.chat.id, open("marshruty-1.jpg", "rb"), caption="Данные взяты с сайта https://sysert.life/")
        else:
            bot.reply_to(message, "Не удалось загрузить изображение")
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {e}")




if __name__ == '__main__':
    bot.polling(none_stop=True)
