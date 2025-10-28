# bot.py
from flask import Flask, request
import telebot
import os, requests, tempfile, shutil
from io import BytesIO
import yt_dlp
import logging

# ---------- CONFIG ----------
TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")
HF_API_KEY = os.getenv("HF_API_KEY", None)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return "✅ Telegram bot is running."

# ---------- COMMANDS ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 "سلام 👋\nمن می‌تونم برات چت کنم، عکس بسازم، کیفیت عکس رو بالا ببرم، آهنگ یا ویدیو از یوتیوب و اینستاگرام دانلود کنم 🎧🎥\n\nدستورها:\n"
                 "- `بساز گربه زیبا`\n"
                 "- `کیفیت` (و بعد عکس بفرست)\n"
                 "- `دانلود آهنگ <نام>`\n"
                 "- `ویدیو <لینک>`")

# ---------- HANDLERS ----------
@bot.message_handler(content_types=['text'])
def handle_text(m):
    text = m.text.strip().lower()

    # Image generation
    if text.startswith("بساز "):
        prompt = m.text.split(" ", 1)[1]
        bot.reply_to(m, "🎨 در حال ساخت تصویر...")
        img = generate_image(prompt)
        if img:
            bot.send_photo(m.chat.id, img)
        else:
            bot.reply_to(m, "❌ خطا در ساخت تصویر.")
        return

    # Upscale photo
    if text.startswith("کیفیت"):
        bot.reply_to(m, "📸 عکس رو بفرست تا کیفیتش رو بالا ببرم.")
        return

    # Music download
    if text.startswith("دانلود آهنگ "):
        query = m.text.split(" ", 2)[2]
        bot.reply_to(m, f"🔎 در حال جستجو برای آهنگ: {query}")
        send_audio(m.chat.id, query)
        return

    # Video download
    if text.startswith("ویدیو ") or text.startswith("video "):
        url = m.text.split(" ", 1)[1]
        bot.reply_to(m, "📹 در حال آماده‌سازی ویدیو، لطفاً صبر کن...")
        send_video(m.chat.id, url)
        return

    # Default: Chat reply
    bot.reply_to(m, generate_text(m.text))

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    bot.reply_to(m, "🔄 در حال ارتقای کیفیت عکس...")
    file_info = bot.get_file(m.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    up = upscale_image(file_url)
    if up:
        bot.send_photo(m.chat.id, up)
    else:
        bot.reply_to(m, "❌ خطا در ارتقای تصویر.")

# ---------- AI / IMAGE ----------
def generate_text(prompt):
    if not HF_API_KEY:
        return "HF_API_KEY تنظیم نشده."
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    url = "https://api-inference.huggingface.co/models/gpt2"
    try:
        r = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=20)
        if r.status_code == 200 and isinstance(r.json(), list):
            return r.json()[0].get("generated_text", "").strip()
        return "خطا در تولید پاسخ."
    except Exception as e:
        logging.error(e)
        return "خطا در ارتباط با سرور."

def generate_image(prompt):
    if not HF_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    try:
        r = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        if r.status_code == 200:
            return BytesIO(r.content)
    except Exception as e:
        logging.error(e)
    return None

def upscale_image(image_url):
    if not HF_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    url = "https://api-inference.huggingface.co/models/caidas/swin2SR-classical-sr-x2-64"
    try:
        r = requests.post(url, headers=headers, json={"inputs": image_url}, timeout=60)
        if r.status_code == 200:
            return BytesIO(r.content)
    except Exception as e:
        logging.error(e)
    return None

# ---------- DOWNLOAD MUSIC / VIDEO ----------
def send_audio(chat_id, query):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
    }
    tmp = tempfile.mkdtemp()
    try:
        with yt_dlp.YoutubeDL({**ydl_opts, "outtmpl": f"{tmp}/%(title)s.%(ext)s"}) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3")
        with open(filename, "rb") as f:
            bot.send_audio(chat_id, f, title=info.get("title", "Song"))
    except Exception as e:
        logging.error(e)
        bot.send_message(chat_id, "❌ خطا در دانلود آهنگ.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def send_video(chat_id, url):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
    }
    tmp = tempfile.mkdtemp()
    try:
        with yt_dlp.YoutubeDL({**ydl_opts, "outtmpl": f"{tmp}/%(title)s.%(ext)s"}) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, "rb") as f:
            bot.send_video(chat_id, f, caption=info.get("title", "ویدیو"))
    except Exception as e:
        logging.error(e)
        bot.send_message(chat_id, "❌ نتونستم ویدیو رو دانلود کنم (ممکنه لینک نامعتبر باشه).")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ---------- RUN ----------
if __name__ == "__main__":
    bot.polling(none_stop=True)
