import os
import aiohttp
import magic  # Для определения mime_type (pip install python-magic)
from io import BytesIO
from PIL import Image
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeImageSize

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
        image_url = image_url.strip()  # Убираем пробелы
    else:
        # Заглушка, если URL пустой
        image_url = "https://i.ibb.co/fVz9rKn/Chat-GPT-Image-Jan-12-2026-09-47-05-PM.png"
    
    channel_entity = await client.get_entity(CHANNEL)
    
    try:
        if image_url:
            # Скачиваем изображение
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Определяем mime_type
                        mime = magic.from_buffer(image_data, mime=True)
                        
                        # Открываем изображение для анализа и конвертации
                        img_stream = BytesIO(image_data)
                        img = Image.open(img_stream)
                        width, height = img.size
                        attributes = [DocumentAttributeImageSize(width, height)]
                        
                        # Если PNG, конвертируем в JPG для лучшей совместимости с Telegram photo
                        if mime == 'image/png':
                            jpg_stream = BytesIO()
                            img.convert('RGB').save(jpg_stream, format='JPEG', quality=85)  # quality=85 для сжатия без потери
                            image_data = jpg_stream.getvalue()
                            mime = 'image/jpeg'
                        
                        # Отправляем как фото
                        await client.send_file(
                            channel_entity,
                            image_data,
                            caption=text,
                            parse_mode="html",
                            mime_type=mime,
                            attributes=attributes,
                            force_document=False  # Принуждаем как photo
                        )
                    else:
                        raise ValueError(f"Не удалось скачать: HTTP {resp.status}")
        else:
            await client.send_message(channel_entity, text, parse_mode="html")
    except Exception as e:
        print(f"Ошибка: {e}")
        # Фолбек: отправляем текст без картинки
        await client.send_message(channel_entity, text, parse_mode="html")

with client:
    client.loop.run_until_complete(main())
