import telebot
import requests
import time

# === Твой Telegram Token ===
bot = telebot.TeleBot("7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc")

# === Настройки сайта ===
SITE_URL = "https://stlmodels.pro/wp-json/wp/v2/posts"
ACF_FIELD_NAME = "download_link"
CACHE_EXPIRATION_SECONDS = 600  # 10 минут

# === Глобальные переменные для кэша ===
cached_link = None
cached_time = 0

# === Функция получения ссылки с кэшированием ===
def get_latest_download_link():
    global cached_link, cached_time

    if cached_link and (time.time() - cached_time) < CACHE_EXPIRATION_SECONDS:
        return cached_link

    try:
        response = requests.get(SITE_URL)
        response.raise_for_status()
        posts = response.json()

        if posts and isinstance(posts, list):
            acf_data = posts[0].get('acf', {})
            link = acf_data.get(ACF_FIELD_NAME)

            if link:
                cached_link = link
                cached_time = time.time()
                return link

    except Exception as e:
        print("Ошибка при получении ссылки:", e)

    return None

# === Обработка команд Telegram ===
@bot.message_handler(commands=['start', 'download'])
def handle_start(message):
    link = get_latest_download_link()
    if link:
        bot.send_message(message.chat.id, f"🔗 Ваша ссылка для скачивания:\n{link}")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось получить ссылку. Попробуйте позже.")

# === Запуск бота ===
bot.polling()
