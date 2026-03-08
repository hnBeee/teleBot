import logging
from datetime import datetime, timedelta
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from utils.validators import is_valid_url
from utils.file_manager import delete_file
from plugins.tools.qr_gen import generate_qr_code
from plugins.ai_chat.brain import get_ai_response

logger = logging.getLogger(__name__)
SESSION_TIMEOUT = timedelta(minutes=10)

def clean_markdown(text: str) -> str:
    """Hapus semua markdown, sisakan teks biasa + emoji."""
    # Hapus bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Hapus italic dengan *
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'\1', text)
    # Hapus italic dengan _
    text = re.sub(r'_(.*?)_', r'\1', text)
    # Hapus heading
    text = re.sub(r'#{1,6}\s+(.*?)(?:\n|$)', r'\1\n', text)
    # Hapus inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text.strip()

async def send_long_message(update: Update, text: str):
    """
    Kirim pesan dengan jaminan terkirim semua bagian.
    - Bersihkan markdown terlebih dahulu.
    - Jika panjang >4096, pecah dan kirim per bagian.
    - Log setiap keberhasilan/kegagalan.
    """
    MAX_LEN = 4096
    try:
        # Bersihkan markdown
        cleaned = clean_markdown(text)
        logger.debug(f"Panjang pesan setelah dibersihkan: {len(cleaned)} karakter")

        if len(cleaned) <= MAX_LEN:
            # Pesan pendek
            try:
                await update.message.reply_text(cleaned)
                logger.debug("Pesan pendek berhasil dikirim")
            except Exception as e:
                logger.error(f"Gagal kirim pesan pendek: {e}")
                await update.message.reply_text("⚠️ Maaf, ada gangguan saat mengirim pesan.")
        else:
            # Pesan panjang, pecah
            parts = [cleaned[i:i+MAX_LEN] for i in range(0, len(cleaned), MAX_LEN)]
            logger.info(f"Pesan dipecah menjadi {len(parts)} bagian")
            for idx, part in enumerate(parts):
                try:
                    await update.message.reply_text(part)
                    logger.debug(f"Bagian {idx+1}/{len(parts)} berhasil dikirim")
                except Exception as e:
                    logger.error(f"Gagal kirim bagian {idx+1}: {e}")
                    await update.message.reply_text(f"⚠️ Gagal mengirim bagian {idx+1} dari pesan.")
                await asyncio.sleep(0.5)  # jeda antar bagian
    except Exception as e:
        logger.error(f"Error di send_long_message: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Terjadi kesalahan internal saat mengirim pesan.")

async def typing_indicator(context: ContextTypes.DEFAULT_TYPE, chat_id: int, task):
    """Kirim status typing setiap 5 detik hingga task selesai."""
    while not task.done():
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(5)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat_id = update.message.chat_id

    # Deteksi link (downloader)
    if is_valid_url(text):
        context.user_data['target_url'] = text
        keyboard = [
            [InlineKeyboardButton("🔥 Kualitas Asli (Best)", callback_data="dl_best")],
            [InlineKeyboardButton("🎬 HD 720p", callback_data="dl_720")],
            [InlineKeyboardButton("📺 Standar 480p", callback_data="dl_480")],
            [InlineKeyboardButton("🎵 Audio Only (MP3)", callback_data="dl_mp3")]
        ]
        await update.message.reply_text(
            "✅ *Link Terdeteksi!*\n\nSilakan pilih resolusi atau format unduhan di bawah ini:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Deteksi QR
    clean_input = text.lstrip("'\" ").strip()
    if clean_input.lower().startswith("/qr"):
        qr_data = clean_input[3:].strip().strip("'\"")
        if not qr_data:
            await update.message.reply_text("💡 *Cara Pakai:* `/qr teks_anda` (tanpa tanda petik)", parse_mode=ParseMode.MARKDOWN)
            return
        status = await update.message.reply_text("⏳ *Sedang membuat QR Code...*", parse_mode=ParseMode.MARKDOWN)
        try:
            path = generate_qr_code(qr_data)
            with open(path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=f"✅ *QR Code Berhasil Dibuat!*\nIsi: `{qr_data}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            delete_file(path)
            await status.delete()
        except Exception as e:
            logger.error(f"Error QR: {e}")
            await status.edit_text(f"❌ *Gagal:* {str(e)}", parse_mode=ParseMode.MARKDOWN)
        return

    # --- AI CHATBOT ---
    try:
        # Kirim typing pertama
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        # Cek sesi percakapan
        last_interaction = context.user_data.get('last_interaction')
        now = datetime.now()
        is_greeting = False
        if last_interaction is None:
            is_greeting = True
        elif now - last_interaction > SESSION_TIMEOUT:
            is_greeting = True
        context.user_data['last_interaction'] = now

        # Tentukan mode: casual jika bukan pertanyaan kompleks
        complex_keywords = ["jelaskan", "apa itu", "bagaimana", "sejarah", "definisi", "perbedaan", "contoh", "mengapa"]
        casual_mode = not any(k in text.lower() for k in complex_keywords)

        # Untuk casual, tidak batasi token (biarkan AI menentukan panjang)
        max_tokens = None  # atau bisa 4096 jika ingin batas atas

        # Catat waktu mulai
        start_time = datetime.now()

        # Jalankan AI dengan timeout 45 detik (lebih lama untuk curhat)
        ai_task = asyncio.create_task(
            get_ai_response(
                prompt=text,
                is_greeting=is_greeting,
                max_tokens=max_tokens,
                casual_mode=casual_mode
            )
        )
        typing_task = asyncio.create_task(typing_indicator(context, chat_id, ai_task))

        try:
            ai_reply = await asyncio.wait_for(ai_task, timeout=45.0)
        except asyncio.TimeoutError:
            logger.error(f"Timeout AI untuk chat {chat_id} setelah 45 detik")
            ai_task.cancel()
            typing_task.cancel()
            await update.message.reply_text("⏳ Maaf, respons AI terlalu lama. Coba lagi nanti.")
            return
        finally:
            if not typing_task.done():
                typing_task.cancel()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Waktu respons AI untuk chat {chat_id}: {elapsed:.2f} detik, panjang respons: {len(ai_reply)} karakter")

        # Kirim balasan (sudah bersih, tanpa parse_mode)
        await send_long_message(update, ai_reply)

    except Exception as e:
        logger.error(f"Error AI Response: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Maaf, saya sedang kesulitan memproses pesan Anda. Silakan coba lagi nanti.")