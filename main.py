import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. RENDER PORT SERVERI ---
async def handle_ping(request):
    return web.Response(text="Kino Bot Render-da 24/7 ishlamoqda! 🚀")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Health-check veb-server {port}-portda ishga tushdi!")

# --- 2. SOZLAMALAR ---
BOT_TOKEN = "8960989758:AAGOUyvtZl7x4LzkD9zSL9duB3RPjPP6kCM"
CHANNEL_ID = -1003823159246
OWNER_ID = 8314147254

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- BAZA VA SHTATLAR ---
USERS_DB = {}
ADMINS = [OWNER_ID]
user_states = {}

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()

# 4. KINOLAR BAZASI
MOVIES_DATABASE = [
    {
        "id": 1,
        "type": "kino",
        "title": "Avatar 2: Suv Yo'li",
        "search_title": "avatar 2 suv yoli avatar",
        "file_id": "BAACAgIAAxkBAAE..."
    }
]

# 5. SERIAL QISMLARI
SEASONS_DATA = {
    "mashaqqatlar_1": {"start": 3, "end": 9},
    "mashaqqatlar_2": {"start": 10, "end": 22},
    "mashaqqatlar_3": {"start": 23, "end": 35},
    "mashaqqatlar_4": {"start": 36, "end": 48},
    "mashaqqatlar_5": {"start": 49, "end": 64},
    
    "dexter_1": {"start": 65, "end": 76},
    "dexter_2": {"start": 77, "end": 88},
    "dexter_3": {"start": 89, "end": 100},
    "dexter_4": {"start": 101, "end": 112},
    "dexter_5": {"start": 113, "end": 124},
    "dexter_6": {"start": 125, "end": 136},
    "dexter_7": {"start": 137, "end": 148},
    "dexter_8": {"start": 149, "end": 157},

    "tungi_borilar_1": {"start": 271, "end": 282},
    "tungi_borilar_2": {"start": 283, "end": 294},
    "tungi_borilar_3": {"start": 295, "end": 319},
    "tungi_borilar_4": {"start": 320, "end": 331},
    "tungi_borilar_5": {"start": 332, "end": 351},
    "tungi_borilar_6": {"start": 352, "end": 371},
}

# --- KEYBOARDLAR ---
def get_main_menu(user_id: int):
    kb = [
        [
            KeyboardButton(text="🎬 Kinolar"),
            KeyboardButton(text="🍿 Seriallar")
        ]
    ]
    
    if user_id in ADMINS:
        kb.append([KeyboardButton(text="📊 Bot ma'lumotlari")])
        
    if user_id == OWNER_ID:
        kb.append([KeyboardButton(text="➕ Admin qo'shish")])
        
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_serials_menu():
    kb = [
        [InlineKeyboardButton(text="🎬 Mashaqqatlar sari", callback_data="show_mashaqqatlar")],
        [InlineKeyboardButton(text="🩺 Dexter", callback_data="show_dexter")],
        [InlineKeyboardButton(text="🐺 Tungi bo'rilar", callback_data="show_tungi_borilar")]
        [InlineKeyboardButton(text="🎬 Yigitlar", callback_data="show_yigitlar")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_mashaqqatlar_seasons_menu():
    kb = [
        [InlineKeyboardButton(text="1-Fasl 🍿", callback_data="play_mashaqqatlar_1")],
        [InlineKeyboardButton(text="2-Fasl 🍿", callback_data="play_mashaqqatlar_2")],
        [InlineKeyboardButton(text="3-Fasl 🍿", callback_data="play_mashaqqatlar_3")],
        [InlineKeyboardButton(text="4-Fasl 🍿", callback_data="play_mashaqqatlar_4")],
        [InlineKeyboardButton(text="5-Fasl 🍿", callback_data="play_mashaqqatlar_5")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_serials")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_dexter_seasons_menu():
    kb = [
        [InlineKeyboardButton(text="1-Fasl 🍿", callback_data="play_dexter_1"), InlineKeyboardButton(text="2-Fasl 🍿", callback_data="play_dexter_2")],
        [InlineKeyboardButton(text="3-Fasl 🍿", callback_data="play_dexter_3"), InlineKeyboardButton(text="4-Fasl 🍿", callback_data="play_dexter_4")],
        [InlineKeyboardButton(text="5-Fasl 🍿", callback_data="play_dexter_5"), InlineKeyboardButton(text="6-Fasl 🍿", callback_data="play_dexter_6")],
        [InlineKeyboardButton(text="7-Fasl 🍿", callback_data="play_dexter_7"), InlineKeyboardButton(text="8-Fasl 🍿", callback_data="play_dexter_8")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_serials")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_tungi_borilar_seasons_menu():
    kb = [
        [InlineKeyboardButton(text="1-Fasl 🍿", callback_data="play_tungi_borilar_1"), InlineKeyboardButton(text="2-Fasl 🍿", callback_data="play_tungi_borilar_2")],
        [InlineKeyboardButton(text="3-Fasl 🍿", callback_data="play_tungi_borilar_3"), InlineKeyboardButton(text="4-Fasl 🍿", callback_data="play_tungi_borilar_4")],
        [InlineKeyboardButton(text="5-Fasl 🍿", callback_data="play_tungi_borilar_5"), InlineKeyboardButton(text="6-Fasl 🍿", callback_data="play_tungi_borilar_6")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_serials")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    
    USERS_DB[user_id] = {
        "active": True, 
        "username": message.from_user.username or message.from_user.first_name
    }
    
    user_states[user_id] = None
    await message.answer(
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Kino va Seriallar botiga xush kelibsiz.\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(user_id)
    )

@dp.message(F.text == "📊 Bot ma'lumotlari")
async def bot_stats_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    
    total_users = len(USERS_DB)
    active_users = 0
    blocked_users = 0
    
    for uid in list(USERS_DB.keys()):
        try:
            await bot.send_chat_action(chat_id=uid, action="typing")
            USERS_DB[uid]["active"] = True
            active_users += 1
        except Exception:
            USERS_DB[uid]["active"] = False
            blocked_users += 1
            
    stats_text = (
        "📊 **BOT STATISTIKASI VA MA'LUMOTLARI**\n\n"
        f"👥 **Jami a'zolar:** `{total_users}` ta\n"
        f"✅ **Faol a'zolar:** `{active_users}` ta\n"
        f"❌ **Botni taqiqlaganlar:** `{blocked_users}` ta\n"
        f"👑 **Adminlar soni:** `{len(ADMINS)}` ta"
    )
    await message.answer(stats_text, parse_mode="Markdown")

@dp.message(F.text == "➕ Admin qo'shish")
async def add_admin_start(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        return
    
    await state.set_state(AdminStates.waiting_for_admin_id)
    
    users_list_text = "👤 **Bot a'zolari ro'yxati (ID va Username):**\n\n"
    for uid, data in USERS_DB.items():
        users_list_text += f"🔹 ID: `{uid}` | @{data['username']}\n"
        
    users_list_text += "\nYangi admin qilmoqchi bo'lgan a me'yoriyning **Telegram ID** raqamini nusxalab, shu yerga yuboring:"
    
    await message.answer(users_list_text, parse_mode="Markdown")

@dp.message(AdminStates.waiting_for_admin_id)
async def process_add_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        return
    
    try:
        new_admin_id = int(message.text.strip())
        
        if new_admin_id in ADMINS:
            await message.answer("⚠️ Ushbu foydalanuvchi allaqachon admin!")
        elif new_admin_id not in USERS_DB:
            await message.answer("❌ Bu ID dagi foydalanuvchi bot bazasida topilmadi. U avval botga /start bosishi kerak.")
        else:
            ADMINS.append(new_admin_id)
            await message.answer(f"✅ `ID: {new_admin_id}` muvaffaqiyatli admin qilindi!", parse_mode="Markdown")
            
            try:
                await bot.send_message(
                    new_admin_id, 
                    "🎉 Siz botga admin qilib tayinlandingiz! Bosh menyuingizga '📊 Bot ma'lumotlari' tugmasi qo'shildi.",
                    reply_markup=get_main_menu(new_admin_id)
                )
            except Exception:
                pass

    except ValueError:
        await message.answer("❌ Iltimos, faqat raqamlardan iborat Telegram ID yuboring!")
        
    await state.clear()

# --- ODDIY BO'LIMLAR ---

@dp.message(F.text == "🎬 Kinolar")
async def movies_section(message: types.Message):
    user_states[message.from_user.id] = "kino"
    await message.answer("🎬 Kinolar bo'limi. Qidirayotgan kino nomini lotinchada kiriting:")

@dp.message(F.text == "🍿 Seriallar")
async def tv_shows_section(message: types.Message):
    user_states[message.from_user.id] = "serial"
    await message.answer(
        "🍿 **Seriallar bo'limi.**\n\n"
        "Tomosha qilmoqchi bo'lgan serialingizni tanlang:",
        reply_markup=get_serials_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "show_mashaqqatlar")
async def mashaqqatlar_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("🎬 **Mashaqqatlar sari** seriali.\n\nFaslni tanlang:", reply_markup=get_mashaqqatlar_seasons_menu(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "show_dexter")
async def dexter_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("🩺 **Dexter** seriali.\n\nFaslni tanlang:", reply_markup=get_dexter_seasons_menu(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "show_tungi_borilar")
async def tungi_borilar_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("🐺 **Tungi bo'rilar** seriali.\n\nFaslni tanlang:", reply_markup=get_tungi_borilar_seasons_menu(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_serials")
async def back_to_serials_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("🍿 **Seriallar bo'limi.**\n\nTomosha qilmoqchi bo'lgan serialingizni tanlang:", reply_markup=get_serials_menu(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("play_"))
async def send_season_episodes(callback: types.CallbackQuery):
    season_key = callback.data.replace("play_", "")
    season_info = SEASONS_DATA.get(season_key)

    if not season_info:
        await callback.answer("❌ Ushbu fasl ma'lumotlari hali yuklanmagan.", show_alert=True)
        return

    await callback.answer()

    for msg_id in range(season_info["start"], season_info["end"] + 1):
        try:
            await bot.copy_message(chat_id=callback.from_user.id, from_chat_id=CHANNEL_ID, message_id=msg_id)
            await asyncio.sleep(0.4)
        except Exception as e:
            logging.error(f"{msg_id}-qismni yuborishda xatolik: {e}")

@dp.message(F.text)
async def search_handler(message: types.Message):
    user_id = message.from_user.id
    query = message.text.strip().lower()
    current_mode = user_states.get(user_id)

    if not current_mode:
        await message.answer("Iltimos, avval **🎬 Kinolar** yoki **🍿 Seriallar** tugmasini bosing!")
        return

    found_item = next((item for item in MOVIES_DATABASE if item["type"] == current_mode and query in item["search_title"]), None)

    if found_item:
        movie_inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⭐ Premium | Yuklab olish", callback_data=f"buy_premium_{found_item['id']}")]]
        )
        await message.answer(f"🎬 **Kino topildi:** {found_item['title']}\n\n📥 Kinoni yuklab olish uchun bosing:", reply_markup=movie_inline_kb, parse_mode="Markdown")
    else:
        await message.answer(f"❌ '{message.text}' bo'yicha {current_mode} topilmadi.")

# --- ISHGA TUSHIRISH (RENDER FRIENDLY) ---
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Render porti uchun veb-serverni yoqamiz
    await start_web_server()
    
    # 2. Telegram Bot Polling-ni yoqamiz
    print("🤖 Aiogram Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
