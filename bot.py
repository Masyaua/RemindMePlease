import telebot
import requests

BOT_TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'  # Заменить на свой токен
bot = telebot.TeleBot(BOT_TOKEN)

REQUIRED_CHANNELS = ['Stuff3D', 'Another3DChannel']  # Каналы, на которые нужно подписаться
SITE_URL = 'https://stlmodels.pro/wp-json/wp/v2/posts'  # URL для получения постов
ACF_FIELD_NAME = 'download_link'  # Поле ACF, где хранится ссылка на файл

def is_subscribed_to_any(user_id):
    """Проверяем, подписан ли пользователь хотя бы на один канал"""
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{channel}&user_id={user_id}"
        res = requests.get(url).json()
        print(f"Проверка подписки для пользователя {user_id} на канал @{channel}: {res}")  # Для отладки
        status = res.get("result", {}).get("status", "")
        if status in ["member", "administrator", "creator"]:
            return True
    return False

def get_latest_download_link():
    """Получаем ссылку на последнюю модель с сайта"""
    response = requests.get(SITE_URL)
    if response.status_code != 200:
        return None
    posts = response.json()
    if not posts:
        return None
    acf_data = posts[0].get('acf', {})
    return acf_data.get(ACF_FIELD_NAME)

@bot.message_handler(commands=['start'])
def start_message(message):
    """Команда /start, приветствие и проверка подписки"""
    user_id = message.chat.id
    if not is_subscribed_to_any(user_id):
        # Если пользователь не подписан на канал, предложим подписаться
        channel_list = '\n'.join([f"👉 https://t.me/{ch}" for ch in REQUIRED_CHANNELS])
        bot.send_message(
            user_id,
            f"❗ Чтобы получить ссылку на модель, подпишись хотя бы на один из этих каналов:\n{channel_list}\n\nПосле подписки используй команду /get для получения ссылки."
        )
    else:
        bot.send_message(user_id, "👋 Привет! Ты подписан на канал(ы). Используй команду /get для получения ссылки на STL-модель.")

@bot.message_handler(commands=['get'])
def send_model(message):
    """Команда /get для получения ссылки на файл"""
    user_id = message.chat.id
    if is_subscribed_to_any(user_id):
        link = get_latest_download_link()
        if link:
            bot.send_message(user_id, f"🔗 Последняя STL-модель:\n{link}")
        else:
            bot.send_message(user_id, "⚠️ Не удалось найти ссылку на файл.")
    else:
        # Если не подписан, повторно предложим подписаться
        channel_list = '\n'.join([f"👉 https://t.me/{ch}" for ch in REQUIRED_CHANNELS])
        bot.send_message(
            user_id,
            f"❗ Чтобы получить ссылку, подпишись хотя бы на один из этих каналов:\n{channel_list}\n\nПосле подписки используй команду /get для получения ссылки."
        )

bot.infinity_polling()
