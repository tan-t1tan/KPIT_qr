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


def to_user(user_id, message, **kwargs):
    bot.send_message(user_id, **kwargs)


@bot.message_handler(commands=['start', 'hint'],
                     func=lambda message: db.get_stage(message.from_user.id) not in ['finished', 'finished_advansed'])
def on_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if username is None: username = 'None'
    if db.user_exists(user_id):
        hint, img = db.get_stage_hint(user_id)
        if hint == 0:
            bot.send_message(user_id, messages.us_finished_simple, reply_markup=advanced_markup)
        elif hint == 1:
            pass
        else:
            if img != '0':
                bot.send_photo(user_id, photo=img, caption=hint,
                               reply_markup=types.ReplyKeyboardRemove(selective=False))
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
    hint, img = db.get_stage_hint(user_id)
    if img != '0':
        bot.send_photo(user_id, photo=img, caption=hint)
    else:
        bot.send_message(user_id, hint)
    if db.is_old_winner(user_id): bot.send_message(user_id, messages.us_start_for_old)


@bot.message_handler(regexp=values.advanced_button_text,
                     func=lambda message: db.get_stage(message.from_user.id) == 'finished')
def advanced_handler(message):
    user_id = message.from_user.id
    result = db.set_advanced(user_id)
    if result == 1:
        admin_bot.to_admins(messages.ad_set_advanced.format(username=db.get_username_by_id(user_id),
                                                            user_id=user_id))

        hint, img = db.get_stage_hint(user_id)
        if img != '0':
            bot.send_photo(user_id, photo=img, caption=hint, reply_markup=types.ReplyKeyboardRemove(selective=False))
        else:
            bot.send_message(user_id, hint, reply_markup=types.ReplyKeyboardRemove(selective=False))



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
        admin_bot.to_admins(messages.ad_already_finished_simple.format(username=db.get_username_by_id(user_id),
                                                                       user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_finished_simple)
    elif result == 2:
        admin_bot.to_admins(messages.ad_wrong_flag.format(username=db.get_username_by_id(user_id),
                                                          user_id=user_id, msg=message.text))
        bot.send_message(user_id, messages.us_wrong_flag)
    elif result == 3:
        admin_bot.to_admins(messages.ad_finished_simple.format(username=db.get_username_by_id(user_id),
                                                               user_id=user_id, msg=message.text,
                                                               ow=db.is_old_winner(user_id)))
        bot.send_message(user_id, messages.us_finished_simple, reply_markup=advanced_markup)
    elif result == 4:
        admin_bot.to_admins(messages.ad_finished_advanced.format(username=db.get_username_by_id(user_id),
                                                                 user_id=user_id, msg=message.text,
                                                                 ow=db.is_old_winner(user_id)))
        bot.send_message(user_id, messages.us_finished_advanced)

    elif result == 5:
        admin_bot.to_admins(messages.ad_flag_correct.format(username=db.get_username_by_id(user_id),
                                                            user_id=user_id, msg=message.text,
                                                            stage=db.get_stage(user_id)))

        hint, img = db.get_stage_hint(user_id)
        if img != '0':
            bot.send_photo(user_id, photo=img, caption=hint)
        else:
            bot.send_message(user_id, hint)

    elif result == 6:
        admin_bot.to_admins(messages.ad_already_finished_advanced.format(username=db.get_username_by_id(user_id),
                                                                         user_id=user_id, msg=message.text))


if __name__ == '__main__':
    bot.infinity_polling()
