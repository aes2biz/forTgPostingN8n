import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STR = os.environ["TELEGRAM_SESSION"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]  # лучше @username

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

async def main():
    await client.start()
    # force dialogs load (optional, но помогает)
    await client.get_dialogs()
    text = os.environ.get("PUBLISH_TEXT")
    image_url = os.environ.get("PICTURE_URL")
    if image_url:
        image_url = image_url.strip()  # Remove leading/trailing whitespace
    channel_entity = await client.get_entity(CHANNEL)
    if image_url:
        await client.send_file(channel_entity, image_url, caption=text, parse_mode="html")
    else:
        await client.send_message(channel_entity, text)

with client:
    client.loop.run_until_complete(main())
