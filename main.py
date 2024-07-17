import requests
import telebot
from telebot import types
bot = telebot.TeleBot('6155476263:AAFyMG6DaokGWflvHHaUAKc0kAF6x0h4uWI')

user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Записатись на зустріч')
    markup.add(item1)

    bot.send_message(message.chat.id, 'Привіт, ' + message.from_user.first_name, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Записатись на зустріч':

            user_data[message.chat.id] = {}
            bot.send_message(message.chat.id, "Чудово, напишіть ваше ім'я", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, get_firstname)
        else:
            bot.send_message(message.chat.id, "Такої команди немає")


def get_firstname(message):
    user_data[message.chat.id]['first_name'] = message.text
    bot.send_message(message.chat.id, "Дякую, напишіть вашу фамілію")
    bot.register_next_step_handler(message, get_lastname)


def get_lastname(message):
    user_data[message.chat.id]['last_name'] = message.text
    bot.send_message(message.chat.id, "Дякую, також напишіть ваш email")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_data[message.chat.id]['email'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    time1 = types.KeyboardButton('11:00-13:30')
    time2 = types.KeyboardButton('14:00-17:00')
    time3 = types.KeyboardButton('17:00-19:00')
    markup.add(time1, time2, time3)
    bot.send_message(message.chat.id, "Оберіть проміжок часу о якій ви хочете отримати дзвінок від нашого спеціаліста", reply_markup=markup)
    bot.register_next_step_handler(message, get_time)

def get_time(message):
    user_data[message.chat.id]['time'] = message.text
    bot.send_message(message.chat.id, "Ви були успішно записані на прийом!", reply_markup=types.ReplyKeyboardRemove())
    send_data_to_crm(user_data[message.chat.id])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Записатись на зустріч')
    markup.add(item1)
    bot.send_message(message.chat.id, "Якщо бажаєте записатися ще раз, натисніть кнопку нижче.", reply_markup=markup)

def send_data_to_crm(data):
    url = 'https://hook.eu2.make.com/lpl68r47bpl5to15jxmgv91a922uyg9a'
    data_file = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'email': data['email'],
        'time': data['time']
    }
    response = requests.post(url, json=data_file)
    if response.status_code == 200:
        print('Дані успішно відправлені')
    else:
        print('Помилка відправки данних')

bot.polling(none_stop=True)
