import telebot

bot = telebot.TeleBot("6782521207:AAGojdYUCbSzfGjVBVF87xTrpJZqWbjbX7Q")
@bot.message_handler()
def Myfunc(message):
    bot.send_message(message.chat.id, "Hi, What's happend?")




bot.infinity_polling(skip_pending=True)
