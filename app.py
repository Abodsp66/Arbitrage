import telebot

bot = telebot.TeleBot("7077125494:AAEfbQ6xjGvyz44aAy2fPVAS_yQFGgmwS44")
@bot.message_handler()
def Myfunc(message):
    bot.send_message(message.chat.id, "Hi, What's happend?")




bot.infinity_polling(skip_pending=True)
