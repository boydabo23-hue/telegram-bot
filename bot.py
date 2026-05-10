import os
import random
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from supabase import create_client

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

CHANNEL = "@ThisIsVero"
GROUP = "@mediaveroh"

USERNAME_BOT = "bitchhubofficialBot"

# MULTI ADMIN
ADMIN_IDS = [
    6818059423,
    7088892275
]

if not TOKEN:
    raise ValueError("TOKEN tidak ditemukan!")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE belum di-set!")

# =========================
# CONNECT SUPABASE
# =========================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================
# GENERATE RANDOM CODE
# =========================

def generate_kode(length=8):
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

# =========================
# CHECK JOIN
# =========================

async def cek_join(user_id, bot):

    try:

        ch = await bot.get_chat_member(
            CHANNEL,
            user_id
        )

        gr = await bot.get_chat_member(
            GROUP,
            user_id
        )

        return (
            ch.status in [
                "member",
                "administrator",
                "creator"
            ]
            and
            gr.status in [
                "member",
                "administrator",
                "creator"
            ]
        )

    except:
        return False

# =========================
# START + AUTO SAVE USER
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    user_id = user.id
    nama = user.first_name

    # SAVE USER
    try:

        supabase.table("users").upsert({
            "id": user_id,
            "username": user.username,
            "first_name": user.first_name
        }).execute()

    except Exception as e:

        print("ERROR SAVE USER:", e)

    args = context.args
    kode = args[0] if args else None

    # =====================
    # CHECK JOIN
    # =====================

    if not await cek_join(user_id, context.bot):

        keyboard = [
            [
                InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{CHANNEL.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "👥 Join Group",
                    url=f"https://t.me/{GROUP.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 Coba Lagi",
                    callback_data="cek"
                )
            ]
        ]

        await update.message.reply_text(
            f"Halo {nama}\n\n"
            "Kamu harus join Channel & Group dulu.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # =====================
    # GET VIDEO
    # =====================

    if kode:

        try:

            data = supabase.table("links") \
                .select("*") \
                .eq("kode", kode) \
                .execute()

            if data.data:

                file_id = data.data[0]["file_id"]

                await context.bot.send_chat_action(
                    chat_id=user_id,
                    action="upload_video"
                )

                await context.bot.send_message(
                    user_id,
                    "🔍 Mengecek akses..."
                )

                await context.bot.send_video(
                    chat_id=user_id,
                    video=file_id,
                    caption="🔥 DONE",
                    protect_content=True
                )

            else:

                await update.message.reply_text(
                    "❌ Link tidak valid"
                )

        except Exception as e:

            await update.message.reply_text(
                f"❌ Error:\n{e}"
            )

    else:

        await update.message.reply_text(
            "selamat datang kembali di asupan vero"
        )

# =========================
# AUTO SAVE VIDEO
# =========================

async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # CEK ADMIN
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:

        await update.message.reply_text(
            "❌ Kamu tidak punya akses upload"
        )

        return

    video = update.message.video

    if not video:
        return

    file_id = video.file_id

    kode = generate_kode()

    # SAVE DATABASE
    try:

        supabase.table("links").insert({
            "kode": kode,
            "file_id": file_id
        }).execute()

        link = f"https://t.me/{USERNAME_BOT}?start={kode}"

        await update.message.reply_text(
            f"✅ Video berhasil disimpan!\n\n🔗 {link}"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error save video:\n{e}"
        )

# =========================
# BROADCAST FOTO + TEXT
# =========================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN ONLY
    if update.effective_user.id not in ADMIN_IDS:
        return

    # LOADING
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    msg = await update.message.reply_text(
        "📡 Memulai broadcast..."
    )

    users = supabase.table("users") \
        .select("*") \
        .execute()

    total = 0
    gagal = 0

    # =====================
    # FOTO + CAPTION
    # =====================

    if update.message.photo:

        photo = update.message.photo[-1].file_id

        caption = update.message.caption or ""

        caption = caption.replace(
            "/broadcast",
            ""
        ).strip()

        for user in users.data:

            try:

                await context.bot.send_photo(
                    chat_id=user["id"],
                    photo=photo,
                    caption=caption
                )

                total += 1

            except:

                gagal += 1

    # =====================
    # TEXT
    # =====================

    else:

        if not context.args:

            await msg.edit_text(
                "❌ Contoh:\n/broadcast Halo semuanya 😎"
            )

            return

        pesan = update.message.text.replace(
            "/broadcast",
            ""
        ).strip()

        for user in users.data:

            try:

                await context.bot.send_message(
                    chat_id=user["id"],
                    text=pesan
                )

                total += 1

            except:

                gagal += 1

    # =====================
    # DONE
    # =====================

    await msg.edit_text(
        f"✅ Broadcast selesai!\n\n"
        f"👥 Berhasil: {total}\n"
        f"❌ Gagal: {gagal}"
    )

# =========================
# BUTTON CHECK
# =========================

async def tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if await cek_join(user_id, context.bot):

        await query.edit_message_text(
            "✅ Sudah join, silakan kirim ulang link 😎"
        )

    else:

        await query.answer(
            "❌ Kamu belum join!",
            show_alert=True
        )

# =========================
# RUN BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("broadcast", broadcast)
)

app.add_handler(
    CallbackQueryHandler(tombol)
)

app.add_handler(
    MessageHandler(filters.VIDEO, save_video)
)

print("Bot aktif...")

app.run_polling()
