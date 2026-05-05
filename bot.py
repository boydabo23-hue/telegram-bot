import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ====== WAJIB: Railway Variables ======
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# ====== OPSIONAL tapi disarankan: Railway Variables ======
# Isi dengan username tanpa spasi. Boleh pakai @ atau tanpa @.
# Contoh: CHANNEL=NutrisiViral18  |  GROUP=bpoindo
CHANNEL = os.getenv("CHANNEL", "").strip()
GROUP = os.getenv("GROUP", "").strip()


def _norm_chat(x: str) -> str:
    """Normalize username to @username, return empty string if not set."""
    if not x:
        return ""
    return x if x.startswith("@") else f"@{x}"


CHANNEL = _norm_chat(CHANNEL)
GROUP = _norm_chat(GROUP)

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def is_joined(client: Client, user_id: int) -> bool:
    """
    Cek apakah user sudah join CHANNEL dan GROUP (kalau di-set).
    Kalau CHANNEL/GROUP kosong, yang kosong dianggap lolos.
    """
    try:
        if CHANNEL:
            await client.get_chat_member(CHANNEL, user_id)
        if GROUP:
            await client.get_chat_member(GROUP, user_id)
        return True
    except Exception:
        return False


def join_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []

    if CHANNEL:
        row.append(InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL.lstrip('@')}"))
    if GROUP:
        row.append(InlineKeyboardButton("Join Group", url=f"https://t.me/{GROUP.lstrip('@')}"))

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("✅ Sudah join", callback_data="check_join")])
    return InlineKeyboardMarkup(buttons)


WELCOME_TEXT = (
    "Halo!\n\n"
    "Untuk menggunakan bot ini, kamu harus join Channel & Group dulu."
)

OK_TEXT = (
    "✅ Mantap! Kamu sudah join.\n\n"
    "Sekarang kamu bisa pakai bot ini."
)


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id

    # Jika CHANNEL/GROUP belum diset, kasih info biar tidak bingung
    if not CHANNEL and not GROUP:
        await message.reply_text(
            "Bot aktif ✅\n\n"
            "Tapi ENV `CHANNEL` dan `GROUP` belum diisi.\n"
            "Isi di Railway Variables kalau mau fitur wajib join."
        )
        return

    if await is_joined(client, user_id):
        await message.reply_text(OK_TEXT)
    else:
        await message.reply_text(WELCOME_TEXT, reply_markup=join_keyboard())


@app.on_callback_query(filters.regex("^check_join$"))
async def check_join_cb(client, callback_query):
    user_id = callback_query.from_user.id

    if await is_joined(client, user_id):
        await callback_query.message.edit_text(OK_TEXT)
        await callback_query.answer("Sudah join ✅", show_alert=False)
    else:
        await callback_query.answer("Kamu belum join semua ya. Join dulu lalu klik lagi.", show_alert=True)


# Contoh command lain (biar kelihatan bot jalan)
@app.on_message(filters.command("ping") & filters.private)
async def ping_handler(client, message):
    user_id = message.from_user.id

    if (CHANNEL or GROUP) and (not await is_joined(client, user_id)):
        await message.reply_text("Kamu wajib join dulu.", reply_markup=join_keyboard())
        return

    await message.reply_text("pong ✅")


app.run()
