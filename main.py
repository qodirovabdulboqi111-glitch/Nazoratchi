import os
from flask import Flask, request
import telebot

# 1. Bot tokenini va Render havolasini sozlash
TOKEN = "8868205892:AAFIcqSfrTTv2iCN6ElJTl6DE760BIg0XVU"
# Bu yerga Render taqdim etgan o'z havolangizni yozing (oxirida / bo'lmasin)
WEBHOOK_URL = "https://onrender.com" 

bot = telebot.TeleBot(TOKEN, threaded=False) # Conflict oldini olish uchun threaded=False qilamiz
app = Flask(__name__)

# 2. Xabarlarni qabul qiluvchi guruh ID raqami (o'zingiz ochgan guruh)
# Guruh ID raqamini aniqlab, manfiy son ko'rinishida yozing (Masalan: -100123456789)
MY_GROUP_ID = -1002222222222 

# 3. Webhook manzili (Telegram so'rovlarini qabul qilish uchun)
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + TOKEN)
    return "Bot muvaffaqiyatli ishlamoqda!", 200

# =========================================================
# 4. XABARLARNI TORTISH VA YO'NALTIRISH MANTIQI
# =========================================================

# Barcha turdagi xabarlarni (matn, rasm, video, audio) kuzatish
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def forward_messages(message):
    try:
        # AGAR XABAR SIZ KUZATAYOTGAN GURUHDA BO'LSA
        # (Bu yerda message.chat.id orqali kelayotgan guruhni ajratib olasiz)
        
        # O'zingiz ochgan guruhga xabarni chiroyli nusxalash (reklamasiz)
        bot.copy_message(
            chat_id=MY_GROUP_ID,          # Qayerga boradi
            from_chat_id=message.chat.id,  # Qaysi guruhdan keldi
            message_id=message.message_id  # Xabar ID-si
        )
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

# =========================================================

if __name__ == "__main__":
    # Render avtomatik ravishda PORT muhitini beradi, bo'lmasa 10000 portda ishlaydi
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
