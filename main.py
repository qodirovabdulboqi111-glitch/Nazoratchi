import telebot
import requests
import os
from groq import Groq

# 1. Telegram botingiz tokeni (@BotFather dan olingan)
BOT_TOKEN = "TELEGRAM_BOT_TOKEN_SHU_YERGA_YOZING"

# 2. Groq API kaliti (console.groq.com dan olingan)
GROQ_API_KEY = "GROQ_API_KEY_SHU_YERGA_YOZING"

bot = telebot.TeleBot(BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# Guruhda taqiqlangan so'zlar ro'yxati
TAQIQLANGAN_SOZLAR = ["bitta kam", "uchta kam", "to'rtta kam", "odam bor", "kam bor", "kam odam", "ikkita kam"]

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Shafyor yuborgan ovozni yuklab olish
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        voice_bytes = requests.get(file_url).content
        
        audio_file = "voice.ogg"
        with open(audio_file, "wb") as f:
            f.write(voice_bytes)

        # Groq Whisper API orqali ovozni matnga o'giriash
        with open(audio_file, "rb") as file:
            translation = groq_client.audio.transcriptions.create(
                file=(audio_file, file.read()),
                model="whisper-large-v3",
                language="uz"
            )
        
        matn = translation.text.lower()
        print(f"Ovoz matni: {matn}") # Server logida ko'rish uchun

        # Matnni tekshirish
        for soz in TAQIQLANGAN_SOZLAR:
            if soz in matn:
                # Shafyorning xabarini o'chirish
                bot.delete_message(message.chat.id, message.message_id)
                break
                
        # Vaqtinchalik faylni o'chirish
        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        print(f"Xatolik: {e}")

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
