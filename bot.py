import telebot
import requests
import feedparser
import re

BOT_TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'
CHANNEL_USERNAME = 'Stuff3D'
RSS_FEED_URL = 'https://stlmodels.pro/feed/'

bot = telebot.TeleBot(BOT_TOKEN)

def is_subscribed(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    res = requests.get(url).json()
    status = res.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

def get_latest_download_link():
    feed = feedparser.parse(RSS_FEED_URL)
    if not feed.entries:
        return None
    post = feed.entries[0]
    links = re.findall(r'(https?://[^\s]+)', post.summary)
    for link in links:
        if 'drive.google.com' in link or 'mega.nz' in link:
            return link
    return None

@bot.message_handler(commands=['get'])
def send_model_link(message):
    user_id = message.chat.id
    if is_subscribed(user_id):
        link = get_latest_download_link()
        if link:
            bot.send_message(user_id, f"🔗 Последняя STL-модель:
{link}")
        else:
            bot.send_message(user_id, "❌ Не удалось найти ссылку в последнем посте.")
    else:
        bot.send_message(user_id, f"❗ Подпишись на канал: https://t.me/{CHANNEL_USERNAME}")

bot.infinity_polling()
