import asyncio
import os
import sys
from aiohttp import web
from PIL import Image
from telethon import TelegramClient

# --- 1. RENDER PORT UCHUN ENGINE ---
async def handle_health_check(request):
    return web.Response(text="Bot Render'da muvaffaqiyatli ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web-server {port}-portda muvaffaqiyatli ishga tushdi.")

# --- 2. TELEGRAM VA SKRIPT SOZLAMALARI ---
API_ID = 36328678
API_HASH = "c1d096506263cdd949c0708b30dda3c3"

SOURCE_CHAT = "https://t.me/bazabazabazass"

TARGET_CHATS = [
    "https://t.me/tarjimatv_v",
    "https://t.me/+zSZA7nG4OHNmYmIy"
]

MY_BOT_LINK = "@tarjima_seriallar_kinolar_hd_bot" 

START_MSG = 2
END_MSG = 41

NEW_THUMBNAIL = "cover.jpg"

SEASON_EPISODES = {
    1: 8, 2: 8, 3: 8, 4: 8, 5: 8
}

client = TelegramClient('my_session', API_ID, API_HASH)

def prepare_thumbnail(path):
    if not os.path.exists(path):
        print(f"⚠️ {path} fayli topilmadi, standart muqova ishlatiladi.")
        return None
    try:
        im = Image.open(path)
        im = im.convert('RGB')
        thumb_path = 'thumb_temp.jpg'
        im.save(thumb_path, 'JPEG')
        return thumb_path
    except Exception as e:
        print(f"⚠️ Rasm tayyorlashda xatolik: {e}")
        return None

# --- 3. REPOSTER JARAYONI ---
async def run_reposter():
    # Telegram mijozini ulash
    await client.start()
    print("✅ Telegram mijoziga muvaffaqiyatli ulanildi!")

    target_entities = []
    for chat in TARGET_CHATS:
        try:
            entity = await client.get_entity(chat)
            target_entities.append(entity)
            print(f"✅ Kanal qo'shildi: {chat}")
        except Exception as e:
            print(f"❌ Kanalni yuklashda xatolik ({chat}): {e}")

    current_season = 1
    current_episode = 1

    thumb_file = prepare_thumbnail(NEW_THUMBNAIL)

    for msg_id in range(START_MSG, END_MSG + 1):
        try:
            print(f"\n📥 Post ID {msg_id} yuklanmoqda...")
            message = await client.get_messages(SOURCE_CHAT, ids=msg_id)
            
            if message and message.media:
                caption = f"🎬 **Yigitlar**\n📌 **{current_season}-fasl | {current_episode}-qism**\n\n🤖 Bot: {MY_BOT_LINK}"

                downloaded_file = await client.download_media(message, file="temp_video.mp4")

                for idx, entity in enumerate(target_entities, start=1):
                    print(f"📤 {idx}-kanalga yuborilmoqda...")
                    await client.send_file(
                        entity,
                        file=downloaded_file,
                        caption=caption,
                        thumb=thumb_file if (thumb_file and os.path.exists(thumb_file)) else None,
                        supports_streaming=True,
                        parse_mode="md"
                    )
                
                print(f"🎉 Post ID: {msg_id} ➔ {current_season}-fasl | {current_episode}-qism yuklandi!")

                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)

                current_episode += 1
                max_episodes = SEASON_EPISODES.get(current_season, 8)
                if current_episode > max_episodes:
                    current_season += 1
                    current_episode = 1

                await asyncio.sleep(3)
            else:
                print(f"⚠️ {msg_id}-postda media topilmadi.")

        except Exception as e:
            print(f"❌ {msg_id}-postda xatolik: {e}")
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")

    if thumb_file and os.path.exists(thumb_file):
        os.remove(thumb_file)

    print("\n🏁 Barcha videolar yuklab bo'lindi!")

# --- 4. MAIN RUNNER ---
async def main():
    # 1-qadam: Veb-serverni port bind qilish uchun darhol ishga tushirish
    await start_web_server()
    
    # 2-qadam: Reposter vazifasini asynchronous background task qilib qo'shish
    loop = asyncio.get_event_loop()
    loop.create_task(run_reposter())
    
    # 3-qadam: Serverni to'xtatmasdan ushlab turish
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
