import os
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button
import aiohttp

# Загрузка .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
CHANNELS = os.getenv("CHANNELS").split(",")

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Проверка подписки на каналы
async def is_user_subscribed(user_id):
    for channel in CHANNELS:
        try:
            participant = await bot.get_participant(f"@{channel}", user_id)
            if participant is None:
                print(f"Пользователь {user_id} не подписан на канал @{channel}")
                return False
        except Exception as e:
            print(f"Ошибка при проверке подписки на канал @{channel} для пользователя {user_id}: {e}")
            return False
    return True

@bot.on(events.NewMessage(pattern="/start"))
async def handle_start(event):
    user_id = event.sender_id
    await event.respond(
        "👋 Привет! Чтобы получить ссылку на файл, подпишись на каналы:",
        buttons=[
            [Button.url(f"📢 {ch}", f"https://t.me/{ch}")] for ch in CHANNELS
        ] + [[Button.inline("🔁 Проверить подписку", b"check_sub")]]
    )

@bot.on(events.CallbackQuery(data=b"check_sub"))
async def handle_check_subscription(event):
    user_id = event.sender_id
    if await is_user_subscribed(user_id):
        await event.edit("✅ Подписка подтверждена! Получаю файл...")
        # Получаем ссылку с WordPress
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{WORDPRESS_URL}/123") as resp:
                    data = await resp.json()
                    link = data.get("acf", {}).get("download_link")
                    if link:
                        await bot.send_message(user_id, f"📥 Вот ваша ссылка:\n{link}")
                    else:
                        await bot.send_message(user_id, "⚠️ Ссылка не найдена в ACF.")
        except Exception as e:
            print("Ошибка при запросе:", e)
            await bot.send_message(user_id, "🚫 Ошибка при получении файла.")
    else:
        await event.answer("❌ Вы не подписались на все каналы.", alert=True)

print("🤖 Бот запущен!")
bot.run_until_disconnected()
