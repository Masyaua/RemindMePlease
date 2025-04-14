import telebot
import requests

BOT_TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'
bot = telebot.TeleBot(BOT_TOKEN)

REQUIRED_CHANNELS = ['Stuff3D', 'Another3DChannel']  # Каналы для подписки
SITE_URL = 'https://stlmodels.pro/wp-json/wp/v2/posts'  # URL для получения постов из сайта
ACF_FIELD_NAME = 'download_link'  # Название поля ACF для ссылки

# Функция проверки подписки пользователя на каналы
def is_subscribed_to_any(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{channel}&user_id={user_id}"
        try:
            res = requests.get(url).json()
            status = res.get("result", {}).get("status", "")
            if status in ["member", "administrator", "creator"]:
                return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для канала {channel}: {e}")
    return False

# Функция для получения последней ссылки на скачивание
def get_latest_download_link():
    try:
        response = requests.get(SITE_URL)
        response.raise_for_status()  # Проверка на успешный ответ
        posts = response.json()
        if not posts:
            return None
        acf_data = posts[0].get('acf', {})
        return acf_data.get(ACF_FIELD_NAME)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса на сайт: {e}")
        return None

# Обработчик команды /get для отправки ссылки на скачивание
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
            f"❗ Чтобы получить ссылку, подпишись хотя бы на один из этих каналов:\n{channel_list}\n\n"
            "После подписки, напиши команду /get снова, чтобы получить ссылку."
        )

# Запуск бота
bot.infinity_polling()
