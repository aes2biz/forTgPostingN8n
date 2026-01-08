import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("TELEGRAM_SESSION")
CHANNEL  = os.environ.get("TELEGRAM_CHANNEL")

text = os.environ.get("PUBLISH_TEXT")
image_url = os.environ.get("PICTURE_URL")

# ⚠ Используем StringSession
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

async def main():
    await client.start()
    if image_url:
        await client.send_file(CHANNEL, image_url, caption=text)
    else:
        await client.send_message(CHANNEL, text)

with client:
    client.loop.run_until_complete(main())
