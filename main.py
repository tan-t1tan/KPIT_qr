import keys
import telebot
import values
import db_connect
from telebot import types
from datetime import datetime


bot = telebot.TeleBot(keys.BOT_TOKEN)
db = db_connect.Database()
db.restart()

start_markup = types.ReplyKeyboardMarkup(row_width=1)
btn1 = types.KeyboardButton('Поехали!')
start_markup.add(btn1)


def to_admins(message):
    for admin in values.admins:
        bot.send_message(admin, message)
    with open('log.txt', 'a') as f:
        f.write(f"{datetime.now().strftime('%A, %d. %B %Y %I:%M%p')}    {message}\n")


@bot.message_handler(commands=['start'])
def on_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if username is None: username = 'None'
    if db.user_exists(user_id):
        bot.send_message(user_id, db.get_stage_hint(user_id), reply_markup=types.ReplyKeyboardRemove(selective=False))
    else:

        bot.send_message(message.from_user.id, values.start_message, reply_markup=start_markup)
        db.add_user(user_id, username)
        to_admins(f'Пользователь {username} ({user_id}) присоединился к игре!')


@bot.message_handler(regexp='Поехали!')
def first_hint(message):
    user_id = message.from_user.id
    bot.send_message(user_id, values.rules, reply_markup=types.ReplyKeyboardRemove(selective=False))
    bot.send_message(user_id, values.how_to_play)
    bot.send_message(user_id, db.get_stage_hint(user_id))


@bot.message_handler(commands=['stage'], func=lambda message: message.from_user.username in values.admins)
def get_stage(message):
    user_id = message.from_user.id
    username = message.text[7:]
    try:
        stage = db.get_stage_by_username(username)
        bot.send_message(user_id, f"Учатник на {stage} этапе")
    except TypeError:
        bot.send_message(user_id, f"Пользователь не участвует")


@bot.message_handler()
def flag(message):
    user_id = message.from_user.id
    if not db.user_exists(user_id):
        bot.send_message(user_id, values.incorrect_start)
    else:
        flag = message.text
        result = db.next_stage(user_id, flag)
        if result == 0:
            to_admins(f'Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал неверный флаг ({flag})')
            bot.send_message(user_id, values.wrong_flag)
        if result == 1:
            to_admins(f'Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал верный флаг ({flag}) и переходит на уровень {db.get_stage(user_id)}.')
            bot.send_message(user_id, db.get_stage_hint(user_id))
        if result == 2:
            pass
        if result == 3:
            to_admins(f'Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал верный флаг ({flag}) и завершил игру.')
            bot.send_message(user_id, values.final)


if __name__ == '__main__':
    bot.infinity_polling()