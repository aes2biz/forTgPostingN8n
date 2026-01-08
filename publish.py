import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("TELEGRAM_SESSION")
CHANNEL  = os.environ.get("TELEGRAM_CHANNEL")

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

async def main():
    await client.start()

    # Получаем текст и ссылку на картинку из переменных окружения
    text = os.environ.get("PUBLISH_TEXT", "")
    image_url = os.environ.get("PICTURE_URL", None)

    # Получаем entity канала для отправки
    channel_entity = await client.get_entity(CHANNEL)

    # Отправка с картинкой или просто текст
    if image_url:
        await client.send_file(channel_entity, image_url, caption=text)
    else:
        await client.send_message(channel_entity, text)

with client:
    client.loop.run_until_complete(main())
