import os
import aiohttp
from io import BytesIO  # Для работы с bytes в Pillow
from PIL import Image  # Для анализа размера изображения
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeImageSize  # Для атрибутов фото

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
                        
                        # Анализируем размер с Pillow
                        try:
                            img = Image.open(BytesIO(image_data))
                            width, height = img.size
                            attributes = [DocumentAttributeImageSize(width, height)]
                        except Exception as attr_error:
                            print(f"Ошибка анализа размера: {attr_error}")
                            attributes = []  # Фолбек без атрибутов
                        
                        # Отправляем как фото (force_document=False, attributes)
                        await client.send_file(
                            channel_entity,
                            image_data,
                            caption=text,
                            parse_mode="html",
                            mime_type='image/png',  # Или 'image/jpeg' если JPG
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
