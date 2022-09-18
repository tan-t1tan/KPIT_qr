import keys
import telebot
import values
import db_connect
from telebot import types


bot = telebot.TeleBot(keys.BOT_TOKEN)
db = db_connect.Database()

start_markup =


@bot.message_handler(commands=['start'])
def on_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if username is None: username = 'None'

    if message.text == '/start': # Start message

        if db.user_exists(user_id):
            bot.send_message(user_id, db.get_stage_hint(user_id))
        else:
            bot.send_message(message.from_user.id, values.start_message)
            db.add_user(user_id, username)
    else: # Check flag
        if not db.user_exists(user_id):
            bot.send_message(user_id, values.wrong_way)
        flag = message.text[7:]
        result = db.next_stage(user_id, flag)
        print(result)
        if result == 0:
            bot.send_message(user_id, values.wrong_flag)
        if result == 1:
            bot.send_message(user_id, db.get_stage_hint(user_id))
        if result == 2:
            pass
        if result == 3:
            bot.send_message(user_id, values.final)


if __name__ == '__main__':
    bot.infinity_polling()