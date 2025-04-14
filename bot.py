import telebot
import requests
from telebot import types

TOKEN = '7662884090:AAGFJzo8TRiXdVPklVD2A0VhMWFsLu6YRDc'
CHANNELS = ['@Amazing_Photoshop', '@Stuff3D']  # сюда вставь свои каналы

bot = telebot.TeleBot(TOKEN)

# Проверка подписки на хотя бы один канал
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(chat_id=channel, user_id=user_id).status
            if status in ['member', 'administrator', 'creator']:
                return True
        except Exception as e:
            print(f"Ошибка при проверке канала {channel}: {e}")
    return False

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if check_subscription(user_id):
        # Подписан — выдаём ссылку
        post_id = message.text.split()[-1] if len(message.text.split()) > 1 else None
        if post_id:
            try:
                res = requests.get(f"https://stlmodels.pro/wp-json/wp/v2/posts/{post_id}")
                data = res.json()
                download_link = data.get('acf', {}).get('download_link')
                if download_link:
                    bot.send_message(user_id, f"✅ Вот ваша ссылка на скачивание:\n{download_link}")
                else:
                    bot.send_message(user_id, "⚠️ Ссылка не найдена в этом посте.")
            except Exception as e:
                print(e)
                bot.send_message(user_id, "Произошла ошибка при получении данных.")
        else:
            bot.send_message(user_id, "Привет! Отправь команду со ссылкой на модель.")
    else:
        # Не подписан — просим подписаться
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 Перейти в канал", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("🔁 Проверить подписку", callback_data="check_sub"))
        bot.send_message(user_id, "🛑 Чтобы получить доступ, подпишись на каналы ниже:", reply_markup=markup)

# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        bot.send_message(user_id, "Теперь вы можете повторно нажать на ссылку, чтобы получить файл.")
    else:
        bot.answer_callback_query(call.id, "❌ Вы ещё не подписались.")
        bot.send_message(user_id, "Пожалуйста, подпишись на каналы и нажми \"Проверить подписку\".")

# Запуск
bot.infinity_polling()
