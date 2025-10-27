from flask import Flask, request
import telebot
import os

TOKEN = "8206649299:AAHspbu9gqW9m-tH6m1xaGo3uceiFQbDdcI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "ربات تلگرام فعاله ✅"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! 👋 ربات فعاله.")

@bot.message_handler(func=lambda m: True)
def reply_all(message):
    if "سلام" in message.text:
        bot.reply_to(message, "سلام رفیق 😄")
    else:
        bot.reply_to(message, "من فقط به سلام جواب میدم 😉")

if __name__ == "__main__":
    bot.polling(none_stop=True)
  Create bot.py
