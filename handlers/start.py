from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan Menu Utama dengan tombol interaktif."""
    
    # Menyusun tombol: 2 di atas, 2 di bawah
    keyboard = [
        [
            InlineKeyboardButton("🎬 Downloader", callback_data="btn_download"),
            InlineKeyboardButton("🔍 QR Generator", callback_data="btn_qr")
        ],
        [
            InlineKeyboardButton("🤖 AI Chatbot", callback_data="btn_ai"),
            InlineKeyboardButton("❓ Bantuan & Info", callback_data="btn_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    nama = update.effective_user.first_name
    pesan = (
        f"🌟 *Selamat Datang, {nama}!* 🌟\n\n"
        "Saya adalah *Bot Universal* versi stabil. Pilih salah satu layanan "
        "unggulan kami di bawah ini untuk memulai:"
    )
    
    await update.message.reply_text(
        pesan, 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )