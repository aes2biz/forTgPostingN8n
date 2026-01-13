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

async def main():
    await client.start()
    
    text = os.environ.get("PUBLISH_TEXT")
    image_url = os.environ.get("PICTURE_URL")
    
    # --- ЛОГИКА ЗАГЛУШКИ ---
    if image_url and image_url.strip():
        image_url = image_url.strip()
    else:
        # Если URL не передан или пустой, используем дефолтную картинку
        print("Image URL not provided, using placeholder.")
        image_url = "https://i.ibb.co/fVz9rKn/Chat-GPT-Image-Jan-12-2026-09-47-05-PM.png"
    
    channel_entity = await client.get_entity(CHANNEL)

    try:
        # Теперь image_url есть всегда (либо ваш, либо заглушка)
        print(f"Downloading image: {image_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    
                    # Открываем изображение
                    img_stream = BytesIO(image_data)
                    img = Image.open(img_stream)
                    
                    # Ресайз (оптимизация)
                    max_size = 1920 
                    if img.width > max_size or img.height > max_size:
                        img.thumbnail((max_size, max_size), Image.LANCZOS)
                        print(f"Resized to {img.size}")
                    
                    # Подготовка потока для отправки
                    jpg_stream = BytesIO()
                    # Конвертируем в RGB и сохраняем в JPEG
                    img.convert('RGB').save(jpg_stream, format='JPEG', quality=90)
                    
                    # Перематываем поток в начало
                    jpg_stream.seek(0)
                    
                    # --- ГЛАВНОЕ ИСПРАВЛЕНИЕ ---
                    # Явно задаем имя файла, чтобы Telegram понял, что это фото
                    jpg_stream.name = "image.jpg"
                    
                    print(f"Sending photo... Size: {jpg_stream.getbuffer().nbytes} bytes")

                    # Отправляем
                    await client.send_file(
                        channel_entity,
                        file=jpg_stream,
                        caption=text,
                        parse_mode="html",
                        force_document=False
                    )
                else:
                    print(f"HTTP Error: {resp.status} for URL: {image_url}")
                    # Если даже заглушка не скачалась — шлем просто текст
                    await client.send_message(channel_entity, text, parse_mode="html")

    except Exception as e:
        print(f"Global Error: {e}")
        # Аварийный фолбек: отправляем текст без картинки
        try:
            await client.send_message(channel_entity, text, parse_mode="html")
        except Exception as msg_e:
            print(f"Failed to send fallback message: {msg_e}")

with client:
    client.loop.run_until_complete(main())
