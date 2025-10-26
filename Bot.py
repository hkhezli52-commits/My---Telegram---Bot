import telebot

TOKEN = "8206649299:AAHspbu9gqW9m-tH6m1xaGo3uceiFQbDdcI"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! 👋 ربات فعاله.")

@bot.message_handler(func=lambda message: True)
def echo(message):
    if "سلام" in message.text:
        bot.reply_to(message, "سلام رفیق 😄")
    else:
        bot.reply_to(message, "من فقط به سلام جواب میدم 😉")

bot.polling()