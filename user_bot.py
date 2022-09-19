import telebot
from res import values, keys
import db_connect
from telebot import types
import admin_bot
from res import messages

bot = telebot.TeleBot(keys.USER_BOT_TOKEN)
db = db_connect.Database(keys.MONGO_AUTH)
db.restart()  # ЗАКОМЕННТИРОВАТЬ ПЕРЕД ДЕПЛОЕМ!!!

start_markup = types.ReplyKeyboardMarkup(row_width=1)
btn1 = types.KeyboardButton(values.start_button_text)
start_markup.add(btn1)

advanced_markup = types.ReplyKeyboardMarkup(row_width=1)
btn1 = types.KeyboardButton(values.advanced_button_text)
advanced_markup.add(btn1)


def to_user(user_id, message):
    bot.send_message(user_id, message)


@bot.message_handler(commands=['start', 'hint'])
def on_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if username is None: username = 'None'
    if db.user_exists(user_id):
        hint = db.get_stage_hint(user_id)
        if hint == 0:
            bot.send_message(user_id, messages.us_finished_simple, reply_markup=advanced_markup)
        elif hint == 1:
            pass
        else:
            bot.send_message(user_id, hint, reply_markup=types.ReplyKeyboardRemove(selective=False))
    else:

        bot.send_message(message.from_user.id, messages.us_start_message, reply_markup=start_markup)
        db.add_user(user_id, username)
        admin_bot.to_admins(messages.ad_new_user.format(username=username, user_id=user_id))


@bot.message_handler(regexp=values.start_button_text, func=lambda message: db.get_stage(message.from_user.id) == 0)
def first_hint(message):
    user_id = message.from_user.id
    bot.send_message(user_id, messages.us_rules, reply_markup=types.ReplyKeyboardRemove(selective=False))
    bot.send_message(user_id, messages.us_how_to_play)
    bot.send_message(user_id, db.get_stage_hint(user_id))


# @bot.message_handler(commands=['stage'], func=lambda message: message.from_user.id in values.admins)
# def get_stage(message):
#     user_id = message.from_user.id
#     username = message.text[7:]
#     try:
#         stage = db.get_stage_by_username(username)
#         bot.send_message(user_id, f"Участник на {stage} этапе")
#     except TypeError:
#         bot.send_message(user_id, f"Пользователь не участвует")


# @bot.message_handler(commands=['send_all'], func=lambda message: message.from_user.id in values.admins)
# def send_all(message):
#     message = message.text[9:]
#     users = db.get_all_users_id()
#     for user in users:
#         bot.send_message(user, message)


# @bot.message_handler(commands=['silent_mode'], func=lambda message: message.from_user.id in values.admins)
# def silent(message):
#     val = message.text[13:]
#     val = not bool(val)
#     to_admins(f'Теперь silent_mode в состоянии {val}.', force=True)
#     values.silent_mode = val


# @bot.message_handler(commands=['RESTART'], func=lambda message: message.from_user.id in values.admins)
# def silent(message):
#     user_id = message.from_user.id
#     username = db.get_username_by_id(user_id)
#     to_admins(f'Пользователь {username} очистил базу данных!')
#     db.restart()


# @bot.message_handler(commands=['for_user'], func=lambda message: message.from_user.id in values.admins)
# def for_user(message):
#     user = message.text.split(' ')[1]
#     user_flag = message.text.split(' ')[2]
#     user_id = db.get_id_by_username(user)
#     result = db.next_stage(user_id, user_flag)
#     if result == 0:
#         to_admins(f'({message.from_user.username})Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал неверный флаг ({user_flag})')
#         bot.send_message(user_id, values.wrong_flag)
#     if result == 1:
#         to_admins(
#             f'({message.from_user.username})Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал верный флаг ({user_flag}) и переходит на уровень {db.get_stage(user_id)}.')
#         bot.send_message(user_id, db.get_stage_hint(user_id))
#     if result == 2:
#         pass
#     if result == 3:
#         to_admins(
#             f'({message.from_user.username})Пользователь {db.get_username_by_id(user_id)} ({user_id}) сдал верный флаг ({user_flag}) и завершил игру.')
#         bot.send_message(user_id, values.final)


@bot.message_handler(regexp=values.advanced_button_text, func=lambda message: db.get_stage(message.from_user.id) == 'finished')
def advanced_handler(message):
    user_id = message.from_user.id
    result = db.set_advanced(user_id)
    if result == 1:
        admin_bot.to_admins(messages.ad_set_advanced.format(username=db.get_username_by_id(user_id),
                                                            user_id=user_id))
    bot.send_message(user_id, db.get_stage_hint(user_id))


@bot.message_handler(commands=['rules'])
def rules_handler(message):
    bot.send_message(message.from_user.id, messages.us_rules)


@bot.message_handler(commands=['how_to_play'])
def htp_handler(message):
    bot.send_message(message.from_user.id, messages.us_how_to_play)


@bot.message_handler()
def flag_handler(message):
    user_id = message.from_user.id
    flag = message.text

    result = db.check_flag(user_id, flag)
    if result == 0:  # No such user
        admin_bot.to_admins(messages.ad_no_such_user.format(username=message.from_user.username,
                                                            user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_no_such_user)
    elif result == 1:  # Already finished
        admin_bot.to_admins(messages.ad_already_finished.format(username=db.get_username_by_id(user_id),
                                                                user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_finished_simple)
    elif result == 2:
        admin_bot.to_admins(messages.ad_wrong_flag.format(username=db.get_username_by_id(user_id),
                                                          user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_wrong_flag)
    elif result == 3:
        admin_bot.to_admins(messages.ad_finished_simple.format(username=db.get_username_by_id(user_id),
                                                               user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_finished_simple, reply_markup=advanced_markup)
    elif result == 4:
        admin_bot.to_admins(messages.ad_finished_advanced.format(username=db.get_username_by_id(user_id),
                                                               user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_finished_advanced)

    elif result == 5:
        admin_bot.to_admins(messages.ad_flag_correct.format(username=db.get_username_by_id(user_id),
                                                                 user_id=user_id, msg=message.text, stage=db.get_stage(user_id)))
        bot.send_message(user_id, db.get_stage_hint(user_id))


def send_message(user_id, message):
    bot.send_message(user_id, message)


if __name__ == '__main__':
    bot.infinity_polling()