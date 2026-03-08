import logging
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from core.config import BOT_TOKEN
from core.logger import setup_logger
from handlers.start import start_command
from handlers.common import handle_text_message
from handlers.menu_handler import handle_callback_query

# Inisialisasi Logger
logger = setup_logger()

async def post_init(application: Application) -> None:
    """Fungsi yang dijalankan sekali saat startup untuk setting menu di pojok kiri bawah."""
    # Menghapus /help sesuai permintaan, hanya menyisakan /start
    commands = [
        BotCommand("start", "Mulai ulang bot & Menu Utama")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Menu bot (Command List) berhasil diperbarui tanpa /help.")

def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN tidak ditemukan di .env")
        return

    # 1. Bangun Aplikasi
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # 2. DAFTARKAN SEMUA HANDLER (Urutan sangat berpengaruh)
    
    # Handler untuk perintah /start
    app.add_handler(CommandHandler("start", start_command))
    
    # Handler UNTUK KLIK TOMBOL (Menangani btn_download, btn_qr, dl_720, dll)
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Handler untuk pesan teks biasa (Link Downloader & AI Chat)
    # filters.TEXT & ~filters.COMMAND artinya menangkap teks yang BUKAN perintah /
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # 3. JALANKAN BOT (Hanya panggil ini SEKALI di akhir)
    logger.info("Bot Universal berhasil dijalankan...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()