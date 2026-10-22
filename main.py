import telebot
import requests
import os
from groq import Groq
from flask import Flask
from threading import Thread
import time

# --- RENDER VEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot faol!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- KALITLAR (SIZNING ASLIY KALITLARINGIZ) ---
API_TOKEN = '8868205892:AAFIcqSfrTTv2iCN6ElJTl6DE760BIg0XVU'
GROQ_API_KEY = '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'

# --- TAQIQLANGAN SO'ZLAR RO'YHATLI ---
TAQIQLANGAN_SOZLAR = ["kam", "pustoy", "bo'sh", "bosh", "pochta", "olamiz"]

bot = telebot.TeleBot(API_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://telegram.org{API_TOKEN}/{file_info.file_path}"
        voice_bytes = requests.get(file_url).content
        
        ogg_filename = f"voice_{message.message_id}_{int(time.time())}.ogg"
        with open(ogg_filename, "wb") as f:
            f.write(voice_bytes)

        with open(ogg_filename, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(ogg_filename, audio_file.read()),
                model="whisper-large-v3",
                language="uz"
            )
        
        matn = transcription.text.lower()
        print(f"ESHITILGAN OVOZ MATNI: {matn}") # Endi bu yozuv aniq Render logida chiqadi
        
        o_chirish_kerak = False
        for soz in TAQIQLANGAN_SOZLAR:
            if soz in matn:
                o_chirish_kerak = True
                break
        
        if o_chirish_kerak:
            bot.delete_message(message.chat.id, message.message_id)
            print("Taqiqlangan so'z topildi va ovoz o'chirildi!")
            
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        if 'ogg_filename' in locals() and os.path.exists(ogg_filename):
            os.remove(ogg_filename)

# --- ASOSIY ISHGA TUSHIRISH TIZIMI ---
if __name__ == "__main__":
    # Veb serverni birinchi parallel oqimda yoqamiz
    t = Thread(target=run_server)
    t.daemon = True
    t.start()
    
    print("Veb server port ochdi...")
    print("Telegram bot xabarlarni tinglashni boshlamoqda...")
    
    # Bot pollingni asosiy oqimda silliq yoqamiz
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
