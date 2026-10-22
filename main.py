import telebot
import requests
import os
from groq import Groq
from flask import Flask
from threading import Thread

# --- RENDER UCHUN VEB SERVER (PORT OCHISH) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    # Render avtomatik taqdim etadigan portni oladi, bo'lmasa 8080 ishlatadi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- SOZLAMALAR ---
# Telegram bot tokenini qo'shtirnoq ichiga yozing:
API_TOKEN ='8868205892:AAEirz_u678yv93BwtnpccoElR6CfT48ibk'

# Groq API kalitini qo'shtirnoq ichiga yozing:
GROQ_API_KEY = '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'

# --- TAQIQLANGAN SO'Z BIRIKMALARI ---
TAQIQLANGAN_BIRIKMALAR = [
    "to'rtta kam", "tortta kam", 
    "uchta kam", 
    "ikkita kam", 
    "bitta kam",
    "pustoymiz", "pustoy", 
    "bo'shadik", "boshadik",
    "ikkita odam olamiz",
    "to'rtta odam olamiz", "tortta odam olamiz",
    "uchta odam olamiz", 
    "bitta odam olamiz",
    "odam pochta olamiz", "odam pochta", "pochta olamiz"
]

bot = telebot.TeleBot(API_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Ovozli xabarni yuklab olish
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://telegram.org{API_TOKEN}/{file_info.file_path}"
        voice_bytes = requests.get(file_url).content
        
        ogg_filename = f"voice_{message.message_id}.ogg"
        with open(ogg_filename, "wb") as f:
            f.write(voice_bytes)

        # Groq API orqali ovozni matnga o'girish
        with open(ogg_filename, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(ogg_filename, audio_file.read()),
                model="whisper-large-v3",
                language="uz"
            )
        
        matn = transcription.text.lower()
        
        # Kalit so'z birikmalarini tekshirish
        o_chirish_kerak = False
        for birikma in TAQIQLANGAN_BIRIKMALAR:
            if birikma in matn:
                o_chirish_recak = True
                o_chirish_kerak = True
                break
        
        # Agar taqiqlangan birikma topilsa, xabarni o'chirish
        if o_chirish_kerak:
            bot.delete_message(message.chat.id, message.message_id)
            
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)

    except Exception as e:
        print(f"Xatolik: {e}")
        if 'ogg_filename' in locals() and os.path.exists(ogg_filename):
            os.remove(ogg_filename)

if __name__ == "__main__":
    print("Veb server ishga tushmoqda...")
    # Veb serverni alohida oqimda yoqamiz (Render talabi)
    server_thread = Thread(target=run)
    server_thread.start()
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)
        
