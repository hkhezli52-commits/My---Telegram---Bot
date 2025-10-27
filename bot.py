from flask import Flask, request
import telebot
import os

TOKEN = "8206649299:AAHspbu9gqW9m-tH6m1xaGo3uceiFQbDdcI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# مسیر webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "ربات فعاله ✅"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! 👋 ربات تلگرام فعاله و روی Render کار می‌کنه 😎")

@bot.message_handler(func=lambda m: True)
def reply_all(message):
    if "سلام" in message.text:
        bot.reply_to(message, "سلام رفیق 😄")
    else:
        bot.reply_to(message, "من فقط به سلام جواب میدم 😉")

# ست کردن webhook
if __name__ == "__main__":
    # لینک سایت Render + توکن
    URL = "https://my-telegram-bot-0b0c.onrender.com"
    bot.remove_webhook()
    bot.set_webhook(url=f"{URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
