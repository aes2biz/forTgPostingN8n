import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelInvalidError

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("TELEGRAM_SESSION")
CHANNEL  = os.environ.get("TELEGRAM_CHANNEL")

text = os.environ.get("PUBLISH_TEXT")
image_url = os.environ.get("PICTURE_URL")

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

async def main():
    await client.start()

    try:
        # Явно получаем peer канала
        channel_entity = await client.get_entity(CHANNEL)

        if image_url:
            await client.send_file(channel_entity, image_url, caption=text)
        else:
            await client.send_message(channel_entity, text)

    except ChannelInvalidError:
        print("❌ Неверный канал или доступ запрещён!")
    except TypeError as e:
        print("❌ Telethon не смог распознать peer:", e)

with client:
    client.loop.run_until_complete(main())
