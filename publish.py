import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

async def main():
    await client.start()

    # Попробуем получить канал (username или ID через get_dialogs)
    await client.get_dialogs()

    # Пытаемся получить entity
    channel_entity = await client.get_entity('@robo_neuro_news')  # предпочитай username

    await client.send_file(channel_entity, image_url, caption=text)

with client:
    client.loop.run_until_complete(main())
