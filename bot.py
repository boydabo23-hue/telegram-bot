import os
import random
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
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
GROUP = "@bpoindo"

USERNAME_BOT = "veronicasexbot"

if not TOKEN:
    raise ValueError("TOKEN tidak ditemukan!")

# =========================
# CONNECT SUPABASE
# =========================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# GENERATE KODE
# =========================

def generate_kode(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# =========================
# CEK JOIN
# =========================

async def cek_join(user_id, bot):
    try:
        ch = await bot.get_chat_member(CHANNEL, user_id)
        gr = await bot.get_chat_member(GROUP, user_id)

        return (
            ch.status in ["member", "administrator", "creator"]
            and
            gr.status in ["member", "administrator", "creator"]
        )

    except:
        return False

# =========================
# BUAT LINK
# =========================

async def buatlink(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Contoh:\n/buatlink video1.mp4"
        )
        return

    nama_video = context.args[0]

    kode = generate_kode()

    # simpan ke database
    supabase.table("links").insert({
        "kode": kode,
        "video": nama_video
    }).execute()

    link = f"https://t.me/{USERNAME_BOT}?start={kode}"

    await update.message.reply_text(
        f"🔗 Link berhasil dibuat:\n\n{link}"
    )

# =========================
# KIRIM VIDEO
# =========================

async def kirim_video(chat_id, video, context):

    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=open(video, "rb"),
            caption="🔥 Nih videonya bro 😏"
        )

    except:
        await context.bot.send_message(
            chat_id,
            "❌ Video tidak ditemukan"
        )

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    nama = update.effective_user.first_name

    args = context.args
    kode = args[0] if args else None

    # =====================
    # CEK JOIN
    # =====================

    if not await cek_join(user_id, context.bot):

        keyboard = [
            [
                InlineKeyboardButton(
                    "Join Dulu",
                    url=f"https://t.me/{CHANNEL.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Join Dulu",
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
            f"Hello {nama}\n\n"
            "*Anda harus bergabung di Channel/Grup saya terlebih dahulu untuk melihat file yang saya bagikan.*\n\n"
            "*Silakan Join ke Channel & Group terlebih dahulu 👇*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        return

    # =====================
    # CEK LINK DATABASE
    # =====================

    if kode:

        try:

            data = supabase.table("links") \
                .select("*") \
                .eq("kode", kode) \
                .execute()

            if data.data:

                video = data.data[0]["video"]

                await kirim_video(
                    user_id,
                    video,
                    context
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
            "Welcome bro 😎"
        )

# =========================
# TOMBOL CEK
# =========================

async def tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if await cek_join(user_id, context.bot):

        await query.edit_message_text(
            "✅ Berhasil! Kirim ulang link ya 😎"
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

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("buatlink", buatlink))
app.add_handler(CallbackQueryHandler(tombol))

print("Bot aktif...")
app.run_polling()
