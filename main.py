import telebot
import requests
import os
from groq import Groq

# --- SOZLAMALAR ---
# 1. Telegram bot tokenini qo'shtirnoq ichiga yozing:
API_TOKEN = '8868205892:AAEcENkgVgajTo7oVgXq1b4lv81MVpA6OwY'

# 2. Groq API kalitini qo'shtirnoq ichiga yozing:
GROQ_API_KEY = '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'

# --- TAQIQLANGAN SO'Z BIRIKMALARI ---
TAQIQLANGAN_BIRIKMALAR = [
    "to'rtta kam", "tortta kam", 
    "uchta kam", 
    "ikkita kam", 
    "bitta kam",
    "pustoymiz", "ertaga olamiz", 
    "bo'shadik", "boshadik",
    "ikkita odam olamiz", "ikkita odam olamiz",
    "to'rtta odam olamiz", "tortta odam olamiz",
    "uchta odam olamiz", 
    "bitta odam olamiz",
    "odam pochta olamiz", "odam pochta", "pochta olamiz", "odam pochta olamiz"
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

        # Groq API orqali ovozni matnga o'girish (O'zbek tili uchun Whisper moduli)
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
                o_chirish_kerak = True
                break
        
        # Agar taqiqlangan birikma topilsa, xabarni o'chirish
        if o_chirish_kerak:
            bot.delete_message(message.chat.id, message.message_id)
            
        # Vaqtinchalik faylni o'chirish
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)

    except Exception as e:
        print(f"Xatolik: {e}")
        if 'ogg_filename' in locals() and os.path.exists(ogg_filename):
            os.remove(ogg_filename)

if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)
    
