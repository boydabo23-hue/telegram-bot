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
GROUP = "@veyyooo"

USERNAME_BOT = "bitchhubofficialBot"

# ID TELEGRAM KAMU
ADMIN_ID = 6818059423

if not TOKEN:
    raise ValueError("TOKEN tidak ditemukan!")

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
# AUTO SAVE VIDEO
# =========================

async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # CEK ADMIN
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
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
    supabase.table("links").insert({
        "kode": kode,
        "file_id": file_id
    }).execute()

    link = f"https://t.me/{USERNAME_BOT}?start={kode}"

    await update.message.reply_text(
        f"✅ Video berhasil disimpan!\n\n🔗 {link}"
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
            f"Hello {nama}\n\n"
            "*Anda harus bergabung di Channel/Grup saya terlebih dahulu untuk melihat file yang saya bagikan.*\n\n"
            "*Silakan Join ke Channel & Group terlebih dahulu 👇*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        return

    # =====================
    # GET VIDEO FROM DB
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

                # =====================
                # SEND PROTECTED VIDEO
                # =====================

                await context.bot.send_video(
                    chat_id=user_id,
                    video=file_id,
                    caption="🔥 Nih videonya bubb💦",
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
            "🔥 Welcome bro 😎"
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

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CallbackQueryHandler(tombol)
)

app.add_handler(
    MessageHandler(filters.VIDEO, save_video)
)

print("Bot aktif...")
app.run_polling()
