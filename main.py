import telebot
import requests
import os
from groq import Groq
from flask import Flask
from threading import Thread

# --- RENDER UCHUN VEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot faol va ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 100% TAYYOR SOZLAMALAR (KALITLAR) ---
API_TOKEN = '8868205892:AAFIcqSfrTTv2iCN6ElJTl6DE760BIg0XVU'
GROQ_API_KEY = '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'

# --- TAQIQLANGAN SO'Z BIRIKMALARI ---
TAQIQLANGAN_BIRIKMALAR = [
    "to'rtta kam", "tortta kam", "uchta kam", "ikkita kam", "bitta kam",
    "pustoymiz", "pustoy", "bo'shadik", "boshadik",
    "ikkita odam olamiz", "to'rtta odam olamiz", "tortta odam olamiz",
    "uchta odam olamiz", "bitta odam olamiz",
    "odam pochta olamiz", "odam pochta", "pochta olamiz"
]

bot = telebot.TeleBot(API_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://telegram.org{API_TOKEN}/{file_info.file_path}"
        voice_bytes = requests.get(file_url).content
        
        ogg_filename = f"voice_{message.message_id}.ogg"
        with open(ogg_filename, "wb") as f:
            f.write(voice_bytes)

        with open(ogg_filename, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(ogg_filename, audio_file.read()),
                model="whisper-large-v3",
                language="uz"
            )
        
        matn = transcription.text.lower()
        
        o_chirish_kerak = False
        for birikma in TAQIQLANGAN_BIRIKMALAR:
            if birikma in matn:
                o_chirish_kerak = True
                break
        
        if o_chirish_kerak:
            bot.delete_message(message.chat.id, message.message_id)
            
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        if 'ogg_filename' in locals() and os.path.exists(ogg_filename):
            os.remove(ogg_filename)

if __name__ == "__main__":
    server_thread = Thread(target=run)
    server_thread.start()
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)
