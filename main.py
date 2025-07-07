from keep_alive import keep_alive
import logging
import asyncio
import schedule
import time
from threading import Thread
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)

# ============ CONFIGURATION ============
BOT_TOKEN = "8121865510:AAE6RO6BMz508Ndm6vWeMbELIH8IlN-WomM"  # Bot utama
ADMIN_ID = 7638053116  # Ganti dengan ID Telegram kamu
CHANNEL_USERNAME = "@ratemegos"  # Username atau ID channel
PROMO_INTERVAL_HOURS = 2  # Interval kirim promo
# =======================================

# Setup logging
logging.basicConfig(level=logging.INFO)

# ========= PROMO MESSAGE FUNCTION =========
PROMO_MESSAGE = """
📸 *Kirim Fotomu & Tampil di Rate Me Gos!*  

Mau fotomu dinilai oleh audience? Seru & anonim loh! 😍  
Caranya gampang banget:  
👉 *Cukup kirim fotomu ke bot ini:* [@Ratemegos_bot](https://t.me/Ratemegos_bot)  

💡 *Foto kamu akan dipost ke channel secara anonim!*  
🔒 Tanpa nama (kalau mau, bisa sertakan ID kalian)  
✅ Aman & seru  
💬 Siap dilihat & dinilai audience! 🔥  

*Admin:* [@vionagosal](https://t.me/vionagosal)
"""

def run_schedule():
    bot = Bot(token=BOT_TOKEN)

    def send_promo():
        bot.send_message(chat_id=CHANNEL_USERNAME, text=PROMO_MESSAGE, parse_mode='Markdown')

    schedule.every(PROMO_INTERVAL_HOURS).hours.do(send_promo)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ========== HANDLE FOTO POST KE CHANNEL ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    caption = message.caption or ""
    caption_lower = caption.lower()

    # Tag otomatis berdasarkan caption
    if "cewek" in caption_lower:
        gender_tag = "#cewek"
    elif "cowok" in caption_lower:
        gender_tag = "#cowok"
    else:
        gender_tag = "#anon"

    final_caption = f"""{caption}

Yuk Rate dari 1 - 10
{gender_tag}

Mau Sumbang?
Chat ajah ke: @Ratemegos_bot"""

    # Post ke channel dengan blur
    await context.bot.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo=message.photo[-1].file_id,
        caption=final_caption,
        has_spoiler=True
    )

    # Konfirmasi ke user
    await message.reply_text("✅ Foto kamu sudah dikirim ke channel!")

    # Forward ke admin juga
    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()
    username_display = f"@{username}" if user.username else username
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"👤 User: `{username_display}` kirim foto.",
        parse_mode='Markdown'
    )
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id)

# ========== HANDLE SEMUA PESAN (FORWARD KE ADMIN) ==========
async def forward_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()
    username_display = f"@{username}" if user.username else username

    if message.text:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 User: `{username_display}` kirim pesan:\n\n{message.text}",
            parse_mode='Markdown'
        )
    elif message.photo:
        # Biarkan handle_photo yang memproses
        return
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 User: `{username_display}` kirim pesan yang tidak dikenali.",
            parse_mode='Markdown'
        )

# ========== MAIN FUNCTION ==========
if __name__ == '__main__':
    # Jalankan thread terpisah untuk auto-promo
    Thread(target=run_schedule, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handler untuk foto (posting + forward)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Handler untuk semua pesan lain (forward ke admin)
    app.add_handler(MessageHandler(filters.ALL, forward_all))

    print("🤖 Bot aktif...")
    # Jaga Replit tetap hidup
    keep_alive()

    app.run_polling()
