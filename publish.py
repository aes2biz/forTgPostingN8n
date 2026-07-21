import os
import aiohttp
from io import BytesIO
from PIL import Image
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STR = os.environ["TELEGRAM_SESSION"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

MAX_CAPTION_LEN = 1024  # Лимит Telegram для подписи к фото

async def main():
    await client.start()
    
    text = os.environ.get("PUBLISH_TEXT", "")
    image_url = os.environ.get("PICTURE_URL")
    
    if image_url and image_url.strip():
        image_url = image_url.strip()
    else:
        print("Image URL not provided, using placeholder.")
        image_url = "https://i.ibb.co/fVz9rKn/Chat-GPT-Image-Jan-12-2026-09-47-05-PM.png"
    
    channel_entity = await client.get_entity(CHANNEL)

    try:
        print(f"Downloading image: {image_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    
                    img_stream = BytesIO(image_data)
                    img = Image.open(img_stream)
                    
                    max_size = 3840 
                    if img.width > max_size or img.height > max_size:
                        img.thumbnail((max_size, max_size), Image.LANCZOS)
                        print(f"Resized to {img.size}")
                    
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (0, 0, 0))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')

                    jpg_stream = BytesIO()
                    img.save(jpg_stream, format='JPEG', quality=100, subsampling=0)
                    jpg_stream.seek(0)
                    jpg_stream.name = "image.jpg"
                    
                    print(f"Sending HQ photo... Size: {jpg_stream.getbuffer().nbytes} bytes")

                    # ✅ Проверяем длину подписи
                    if len(text) <= MAX_CAPTION_LEN:
                        # Текст влезает — отправляем одним сообщением
                        await client.send_file(
                            channel_entity,
                            file=jpg_stream,
                            caption=text,
                            parse_mode="html",
                            force_document=False
                        )
                    else:
                        # Текст слишком длинный — фото без подписи, текст отдельно
                        print(f"Caption too long ({len(text)} chars), sending photo and text separately.")
                        await client.send_file(
                            channel_entity,
                            file=jpg_stream,
                            caption="",
                            force_document=False
                        )
                        await client.send_message(
                            channel_entity,
                            text,
                            parse_mode="html"
                        )

                else:
                    print(f"HTTP Error: {resp.status}")
                    await client.send_message(channel_entity, text, parse_mode="html")

    except Exception as e:
        print(f"Global Error: {e}")
        try:
            await client.send_message(channel_entity, text, parse_mode="html")
        except Exception:
            pass

with client:
    client.loop.run_until_complete(main())
