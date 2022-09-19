from res import values, keys, messages
import db_connect
import telebot
import user_bot
from datetime import datetime

admin_bot = telebot.TeleBot(keys.ADMIN_BOT_TOKEN)
db = db_connect.Database(keys.ADMIN_MONGO_AUTH)


def to_admins(message):
    for admin in values.admins:
        try:
            admin_bot.send_message(admin, message)
        except:
            pass
    try:
        with open('log.txt', 'a') as f:
            f.write(f"{datetime.now().strftime('%A, %d. %B %Y %I:%M%p')}    {message}\n")
    except:
        pass


@admin_bot.message_handler(func=lambda message: message.from_user.id in values.admins)
def get_command(message):
    sender = message.from_user.id
    command = message.text.split(' ')[0]

    if command == '/start':
        pass

    elif command == '/send_all':
        users = db.get_all_users()
        msg = message.text.split(' ', 1)[1]
        to_admins(messages.ad_send_all.format(username=message.from_user.username, msg=msg))
        for user in users:
            user_bot.to_user(user, msg)

    elif command == '/send_user':
        username = message.text.split(' ', 2)[1]
        user_id = db.get_id_by_username(username)
        if user_id == 0:
            admin_bot.send_message(sender, messages.ad_no_such_user)
        msg = message.text.split(' ', 2)[2]
        to_admins(messages.ad_send_user.format(username=username, user_id=user_id, msg=msg))

        user_bot.to_user(user_id, msg)

    elif command == '/stage':
        username = message.text.split(' ', 1)[1]
        user_id = db.get_id_by_username(username)
        if user_id == 0:
            admin_bot.send_message(sender, messages.ad_no_such_user)
        stage = db.get_stage(user_id)
        admin_bot.send_message(sender, messages.ad_user_stage.format(username=username, user_id=user_id, stage=stage))

    elif command == '/RESTART__':
        db.restart()

    elif command == '/old_winner':
        username = message.text.split(' ', 1)[1]
        user_id = db.get_id_by_username(username)
        ow = db.is_old_winner(user_id)
        admin_bot.send_message(sender, messages.ad_user_stage.format(ow=ow))


if __name__ == '__main__':
    admin_bot.infinity_polling()
