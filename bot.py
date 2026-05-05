import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ambil token dari Railway
TOKEN = os.getenv("TOKEN")

# ganti sesuai punyamu
CHANNEL = "@NutrisiViral18"
GROUP = "@bpoindo"

# nama file HARUS ada di repo GitHub kamu
FILE_NAME = "file.pdf"

if not TOKEN:
    raise ValueError("TOKEN tidak ditemukan di Railway!")

# cek apakah user sudah join
async def cek_join(user_id, bot):
    try:
        ch = await bot.get_chat_member(CHANNEL, user_id)
        gr = await bot.get_chat_member(GROUP, user_id)

        return ch.status in ["member", "administrator", "creator"] and \
               gr.status in ["member", "administrator", "creator"]
    except:
        return False

# command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await cek_join(user_id, context.bot):
        keyboard = [
            [
                InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL.replace('@','')}"),
                InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP.replace('@','')}")
            ],
            [
                InlineKeyboardButton("✅ Sudah Join", callback_data="cek")
            ]
        ]

        await update.message.reply_text(
            "🔥 *HALO BRO!* 🔥\n\n"
            "Untuk lanjut, kamu wajib join dulu ya 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await kirim_file(update.effective_chat.id, context)

# fungsi kirim file
async def kirim_file(chat_id, context):
    await context.bot.send_message(
        chat_id=chat_id,
        text="🔥 *AKSES DIBUKA!* 🔥\n\nIni konten kamu 👇",
        parse_mode="Markdown"
    )

    await context.bot.send_document(
        chat_id=chat_id,
        document=open(FILE_NAME, "rb"),
        caption="😏 Jangan disebar ya bro..."
    )

# tombol "Sudah Join"
async def tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await cek_join(user_id, context.bot):
        await query.edit_message_text("✅ Berhasil! Mengirim konten...")

        await kirim_file(query.message.chat.id, context)
    else:
        await query.answer("❌ Kamu belum join semua!", show_alert=True)

# run bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(tombol))

print("Bot aktif...")
app.run_polling()
