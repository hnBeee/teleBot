from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_downloader_keyboard() -> InlineKeyboardMarkup:
    """Membuat tombol pilihan resolusi sesuai downloader.py."""
    keyboard = [
        [InlineKeyboardButton("🔥 Kualitas Asli (Best)", callback_data="dl_best")],
        [InlineKeyboardButton("🎬 HD 720p", callback_data="dl_720")],
        [InlineKeyboardButton("📺 Standar 480p", callback_data="dl_480")],
        [InlineKeyboardButton("🎵 Audio Only (MP3)", callback_data="dl_mp3")]
    ]
    return InlineKeyboardMarkup(keyboard)