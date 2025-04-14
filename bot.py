import telebot
import requests

BOT_TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'
bot = telebot.TeleBot(BOT_TOKEN)

REQUIRED_CHANNELS = ['Stuff3D', 'Another3DChannel']
SITE_URL = 'https://stlmodels.pro/wp-json/wp/v2/posts'
ACF_FIELD_NAME = 'download_link'

def is_subscribed_to_any(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{channel}&user_id={user_id}"
        res = requests.get(url).json()
        status = res.get("result", {}).get("status", "")
        if status in ["member", "administrator", "creator"]:
            return True
    return False

def get_latest_download_link():
    response = requests.get(SITE_URL)
    if response.status_code != 200:
        return None
    posts = response.json()
    if not posts:
        return None
    acf_data = posts[0].get('acf', {})
    return acf_data.get(ACF_FIELD_NAME)

@bot.message_handler(commands=['get'])
def send_model(message):
    user_id = message.chat.id
    if is_subscribed_to_any(user_id):
        link = get_latest_download_link()
        if link:
            bot.send_message(user_id, f"🔗 Последняя STL-модель:\n{link}")
        else:
            bot.send_message(user_id, "⚠️ Не удалось найти ссылку на файл.")
    else:
        channel_list = '\n'.join([f"👉 https://t.me/{ch}" for ch in REQUIRED_CHANNELS])
        bot.send_message(user_id,
            f"❗ Чтобы получить ссылку, подпишись хотя бы на один из этих каналов:\n{channel_list}"
        )

bot.infinity_polling()
