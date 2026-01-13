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
    
    if image_url:
        image_url = image_url.strip()
    
    # Получаем сущность канала (лучше делать это один раз)
    try:
        channel_entity = await client.get_entity(CHANNEL)
    except Exception as e:
        print(f"Error getting entity: {e}")
        return

    try:
        if image_url:
            print(f"Downloading image: {image_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Открываем изображение
                        img_stream = BytesIO(image_data)
                        img = Image.open(img_stream)
                        
                        # --- Логика ресайза (опционально, но полезно для скорости) ---
                        # Telegram сжимает фото сам, но если картинка > 10МБ, он ее не примет как фото.
                        # Ваш ресайз до 1024 безопасен, хотя для HD можно и 1920.
                        max_size = 1920 # Увеличил до стандарта HD, чтобы качество было лучше
                        if img.width > max_size or img.height > max_size:
                            img.thumbnail((max_size, max_size), Image.LANCZOS)
                            print(f"Resized to {img.size}")
                        
                        # --- КРИТИЧЕСКИЙ МОМЕНТ ---
                        jpg_stream = BytesIO()
                        # Конвертируем в RGB (на случай PNG с прозрачностью) и сохраняем в поток
                        img.convert('RGB').save(jpg_stream, format='JPEG', quality=90)
                        
                        # Перематываем поток в начало
                        jpg_stream.seek(0)
                        
                        # !!! ВОТ РЕШЕНИЕ !!!
                        # Мы явно говорим библиотеке, что этот поток — файл с именем image.jpg
                        jpg_stream.name = "image.jpg"
                        
                        print(f"Sending photo... Size: {jpg_stream.getbuffer().nbytes} bytes")

                        # Отправляем
                        await client.send_file(
                            channel_entity,
                            file=jpg_stream,     # Передаем поток с именем, а не байты
                            caption=text,
                            parse_mode="html",
                            force_document=False # Теперь это сработает, так как есть .jpg
                        )
                    else:
                        print(f"HTTP Error: {resp.status}")
                        # Фолбек на текст, если картинка не скачалась
                        await client.send_message(channel_entity, text, parse_mode="html")
        else:
            # Если URL нет, просто шлем текст
            await client.send_message(channel_entity, text, parse_mode="html")

    except Exception as e:
        print(f"Global Error: {e}")
        # Фолбек на случай любой ошибки (например, битая картинка)
        try:
            await client.send_message(channel_entity, text, parse_mode="html")
        except Exception as msg_e:
            print(f"Failed to send fallback message: {msg_e}")

with client:
    client.loop.run_until_complete(main())
