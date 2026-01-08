from telethon import TelegramClient
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("TELEGRAM_SESSION")
CHANNEL  = os.environ.get("CHANNEL")

text = os.environ.get("PUBLISH_TEXT")
image_url = os.environ.get("PICTURE_URL")

client = TelegramClient(SESSION, API_ID, API_HASH)

async def main():
    await client.start()
    if image_url:
        await client.send_file(CHANNEL, image_url, caption=text)
    else:
        await client.send_message(CHANNEL, text)

with client:
    client.loop.run_until_complete(main())
