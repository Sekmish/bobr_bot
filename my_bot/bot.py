import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, YANDEX_API_KEY
from extensions import BusSchedule, APIException
from connect_db import DatabaseHandler
from datetime import datetime
import pytz
import requests
from telebot import types


bot = telebot.TeleBot(TOKEN)

# Функция для подключения к базе данных
db_handler = DatabaseHandler()

def connect_to_db():
    db_handler.connect()
    conn = db_handler.conn
    cursor = db_handler.cursor
    return conn, cursor

def disconnect_from_db(conn, cursor):
    db_handler.disconnect()


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    instructions = "Привет! Я информационный бот поселка Бобровский!.\n\n" \
                   "Выберите, что вас интересует:"

    # Создание клавиатуры с кнопками
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    bus_schedule_button = KeyboardButton('/bus_schedule - Расписание автобусов')
    hospital_button = KeyboardButton('/hospitals - Больницы в Бобровском')
    keyboard.add(bus_schedule_button, hospital_button)

    bot.reply_to(message, instructions, reply_markup=keyboard)


@bot.message_handler(commands=['bus_schedule'])
def handle_bus_schedule(message):
    instructions = "Выберите тип расписания автобусов:"

    # Создание клавиатуры с кнопками
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    bus_plus_button = KeyboardButton('/bus_plus - Расписание пригородных автобусов Екатеринбург - Бобровский (ООО "Авто-Плюс" г.Екатеринбург)')
    bus_113_button = KeyboardButton('/bus_113 - Расписание маршрута №113')
    back_button = KeyboardButton('/start - Назад')
    keyboard.add(bus_plus_button, bus_113_button, back_button)

    bot.send_message(message.chat.id, instructions, reply_markup=keyboard)

@bot.message_handler(commands=['hospitals'])
def handle_hospitals(message):
    instructions = "Выберите населенный пункт:"

    # Создание клавиатуры с кнопками
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    hospital_bobr = KeyboardButton('/hospitals_bobr - Больницы в Бобровском')
    hospital_sisert = KeyboardButton('/hospital_sisert - Больницы в Сысерти')
    back_button = KeyboardButton('/start - Назад')
    keyboard.add(hospital_bobr, hospital_sisert, back_button)

    bot.send_message(message.chat.id, instructions, reply_markup=keyboard)


@bot.message_handler(commands=['hospitals_bobr'])
def handle_hospitals_bobr(message):
    instructions = "Выберите больницу:"

    # Создание клавиатуры с кнопками
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    bolnica = KeyboardButton('/bub - Бобровская участковая больница')
    bolnica_kid = KeyboardButton('/bolnica_kid - Детская больница')
    back_button = KeyboardButton('/start - Назад')
    keyboard.add(bolnica, bolnica_kid, back_button)

    bot.send_message(message.chat.id, instructions, reply_markup=keyboard)


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

@bot.message_handler(commands=['bub'])
def handle_bolnica(message):
    try:
        # Подключение к базе данных
        conn, cursor = connect_to_db()

        # Выполнение запроса к базе данных для команды /bolnica
        cursor.execute("SELECT address, phone, working_hours, description FROM organizations WHERE id='1'")
        result = cursor.fetchone()

        # Формирование ответа
        phone = result[1].replace(" ", "")  # Удаление пробелов из номера телефона
        response = f"Адрес: {result[0]}\nТелефон: {phone}\nВремя работы: {result[2]}\nОписание: {result[3]}"

        # Закрытие соединения
        disconnect_from_db(conn, cursor)

        # Отправка ответа пользователю
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {e}")

@bot.message_handler(commands=['bolnica_kid'])
def handle_bolnica_detskaya(message):
    try:
        # Подключение к базе данных
        conn, cursor = connect_to_db()

        # Выполнение запроса к базе данных для команды /bolnica_detskaya
        cursor.execute("SELECT address, phone, working_hours, description FROM organizations WHERE name='Детская больница'")
        result = cursor.fetchone()

        # Формирование ответа
        response = f"Адрес: {result[0]}\nТелефон: {result[1]}\nВремя работы: {result[2]}\nОписание: {result[3]}"

        # Закрытие соединения
        disconnect_from_db(conn, cursor)

        # Отправка ответа пользователю
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {e}")


if __name__ == '__main__':
    bot.polling(none_stop=True)

