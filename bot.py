from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8577228984:AAH8pi61W5pp7LEQiM9hiPHfogQotXbqzUo"
CHANNEL = "@NutrisiViral18"
GROUP = "@bpoindo"

async def cek_join(user_id, bot):
    try:
        ch = await bot.get_chat_member(CHANNEL, user_id)
        gr = await bot.get_chat_member(GROUP, user_id)

        return ch.status in ["member", "administrator", "creator"] and \
               gr.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await cek_join(user_id, context.bot):
        keyboard = [
            [
                InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL.replace('@','')}"),
                InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP.replace('@','')}")
            ],
            [
                InlineKeyboardButton("🔄 Coba Lagi", callback_data="cek")
            ]
        ]

        await update.message.reply_text(
            "⚠️ Anda harus join dulu ya!\n\nKlik tombol di bawah 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("✅ Akses berhasil! Welcome 🎉")

async def tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await cek_join(user_id, context.bot):
        await query.edit_message_text("✅ Berhasil! Kamu sudah join 🎉")
    else:
        await query.answer("❌ Kamu belum join!", show_alert=True)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(tombol))

print("Bot aktif...")
app.run_polling()