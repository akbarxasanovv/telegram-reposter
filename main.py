import asyncio
import os
from aiohttp import web
from PIL import Image
from telethon import TelegramClient

# --- 1. HEALTH-CHECK SERVER ---
async def handle_health_check(request):
    return web.Response(text="Bot ishlayapti!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Server {port}-portda ishga tushdi.")


# --- 2. SOZLAMALAR ---
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

# Fayl nomi GitHub'dagi faylingiz bilan 100% bir xil bo'lishi shart!
client = TelegramClient('my_session', API_ID, API_HASH)


def prepare_thumbnail(path):
    if not os.path.exists(path):
        print("⚠️ cover.jpg fayli topilmadi!")
        return None
    try:
        im = Image.open(path)
        im = im.convert('RGB')
        thumb_path = 'thumb_temp.jpg'
        im.save(thumb_path, 'JPEG')
        return thumb_path
    except Exception as e:
        print(f"⚠️ Rasm xatosi: {e}")
        return None


# --- 3. ASOSIY REPOSTER ---
async def run_reposter():
    try:
        print("🔄 Telegram akkauntga ulanish boshlandi...")
        await client.start()
        print("✅ Telegram akkauntga MUVAFFAQIYATLI ulanindi!")

        target_entities = []
        for chat in TARGET_CHATS:
            try:
                print(f"🔍 Kanal tekshirilmoqda: {chat}")
                entity = await client.get_entity(chat)
                target_entities.append(entity)
                print(f"✅ Kanal muvaffaqiyatli yuklandi: {chat}")
            except Exception as e:
                print(f"❌ Kanalni yuklashda xatolik ({chat}): {e}")

        current_season = 1
        current_episode = 1

        thumb_file = prepare_thumbnail(NEW_THUMBNAIL)

        for msg_id in range(START_MSG, END_MSG + 1):
            try:
                print(f"\n📩 Post ID {msg_id} manba kanalidan olinmoqda...")
                message = await client.get_messages(SOURCE_CHAT, ids=msg_id)
                
                if message and message.media:
                    caption = f"🎬 **Yigitlar**\n📌 **{current_season}-fasl | {current_episode}-qism**\n\n🤖 Bot: {MY_BOT_LINK}"

                    print(f"📥 Post ID {msg_id} video fayli yuklab olinmoqda...")
                    downloaded_file = await client.download_media(message, file="temp_video.mp4")
                    print(f"✅ Video yuklab olindi!")

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
                    
                    print(f"🎉 Post ID: {msg_id} ➔ Yigitlar {current_season}-fasl | {current_episode}-qism barcha kanallarga joylandi!")

                    if os.path.exists(downloaded_file):
                        os.remove(downloaded_file)

                    current_episode += 1
                    max_episodes = SEASON_EPISODES.get(current_season, 8)
                    if current_episode > max_episodes:
                        current_season += 1
                        current_episode = 1

                    await asyncio.sleep(3)
                else:
                    print(f"⚠️ {msg_id}-postda media topilmadi yoki post bo'sh.")

            except Exception as e:
                print(f"❌ {msg_id}-postda xatolik yuz berdi: {e}")
                if os.path.exists("temp_video.mp4"):
                    os.remove("temp_video.mp4")

        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)

        print("\n🏁 Barcha postlar tugadi!")

    except Exception as e:
        print(f"🔥 Telegram ulanishda jiddiy xatolik: {e}")


async def main():
    await start_web_server()
    asyncio.create_task(run_reposter())
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
