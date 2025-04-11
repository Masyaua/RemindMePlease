import telebot
import requests

BOT_TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'
CHANNEL_USERNAME = 'Stuff3D'  # без @
DOWNLOAD_LINK = 'https://drive.google.com/...'  # или Mega

bot = telebot.TeleBot(BOT_TOKEN)

def is_subscribed(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    res = requests.get(url).json()
    status = res.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

@bot.message_handler(commands=['start', 'get'])
def send_file(message):
    user_id = message.chat.id
    if is_subscribed(user_id):
        bot.send_message(user_id, f"✅ Спасибо за подписку! Вот ссылка на скачивание:\n{DOWNLOAD_LINK}")
    else:
        bot.send_message(user_id, f"❗ Сначала подпишись на наш канал: https://t.me/{CHANNEL_USERNAME}\nЗатем нажми /get")

bot.polling()
