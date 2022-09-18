import keys
import telebot
import values
import db_connect

bot = telebot.TeleBot(keys.BOT_TOKEN)
db = db_connect.Database()


@bot.message_handler(commands=['start'])
def on_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    if message.text == '/start': # Start message
        if username is None: username = 'None'

        if db.user_exists(user_id):
            bot.send_message(user_id, 'Hi!')
        else:
            bot.send_message(message.from_user.id, values.start_message)
            db.add_user(user_id, username)
    else: # Check flag
        flag = message.text[6:]
        result = db.next_stage(user_id, flag)




if __name__ == '__main__':
    bot.infinity_polling()