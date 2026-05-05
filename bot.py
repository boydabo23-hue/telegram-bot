import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("8577228984:AAH8pi61W5pp7LEQiM9hiPHfogQotXbqzUo")

CHANNEL = os.getenv("@NutrisiViral18")  # tanpa @
GROUP = os.getenv("@bpoindo")      # tanpa @

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_joined(client, user_id):
    try:
        await client.get_chat_member(CHANNEL, user_id)
        await client.get_chat_member(GROUP, user_id)
        return True
    except:
        return False

@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user

    if not await is_joined(client, user.id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL}")],
            [InlineKeyboardButton("Join Group", url=f"https://t.me/{GROUP}")],
            [InlineKeyboardButton("Coba Lagi", callback_data="cek")]
        ])

        await message.reply_text(
            f"Halo {user.mention}\n\n"
            "Silakan join channel & group dulu ya.",
            reply_markup=buttons
        )
        return

    await message.reply_text("✅ Kamu sudah join! Akses diterima.")

@app.on_callback_query(filters.regex("cek"))
async def cek(client, callback_query):
    user = callback_query.from_user

    if await is_joined(client, user.id):
        await callback_query.message.edit_text("✅ Sudah join! Akses diterima.")
    else:
        await callback_query.answer("Kamu belum join!", show_alert=True)

app.run()
