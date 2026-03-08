import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from plugins.downloader.engine import execute_ytdlp
from utils.file_manager import delete_file

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    # Logika Download (Resolusi)
    if data.startswith("dl_"):
        url = context.user_data.get('target_url')
        if not url:
            await query.message.edit_text("❌ Sesi habis, kirim ulang linknya.")
            return

        await query.message.edit_text("⏳ Sedang mengunduh... Mohon tunggu.")
        result = await asyncio.to_thread(execute_ytdlp, url, data)
        
        if result['error']:
            await query.message.edit_text(f"❌ {result['error']}")
            return

        file_path = result['path']
        try:
            with open(file_path, 'rb') as f:
                if data == 'dl_mp3':
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f)
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, supports_streaming=True)
            await query.message.delete()
        except Exception as e:
            await query.message.edit_text(f"❌ Gagal kirim: {e}")
        finally:
            delete_file(file_path)
            context.user_data.pop('target_url', None)
        return

    if data == "btn_download":
        teks = (
            "📥 *Fitur Video Downloader*\n\n"
            "Cukup kirimkan tautan video dari YouTube, TikTok, atau Instagram. "
            "Saya akan otomatis memproses dan mengirimkan videonya kepada Anda."
        )
    elif data == "btn_qr":
        teks = (
            "🔍 *Fitur QR Generator*\n\n"
            "Gunakan perintah `/qr` diikuti dengan teks atau link di dalam **tanda petik**.\n\n"
            "📌 *Contoh:* `'/qr halo dunia'`\n"
            "📌 *Contoh:* `'/qr https://google.com'`\n\n"
            "Pastikan menggunakan tanda petik agar pesan diproses dengan benar!"
        )
    elif data == "btn_ai":
        teks = (
            "🤖 *Fitur AI Chatbot*\n\n"
            "Sekarang Anda bisa langsung bertanya apa saja kepada saya!\n\n"
            "✨ *Bisa bantu apa saja?*\n"
            "• Nemenin Yapping\n"
            "• Chatting santai\n"
            "• Curhat jua bisa kalo lagi Mood HEHE\n"
            "• Bantu ngerjain tugas\n"
            "• Nanya Hal menarik/Ide\n"
            "• Minta Saran Rekomendasi\n"
            "Cukup ketik pesan Anda langsung di bawah tanpa simbol apa pun."
        )
    elif data == "btn_help":
        teks = (
            "📖 *Panduan Penggunaan Bot*\n\n"
            "1. *Download*: Tempel link video langsung di chat.\n"
            "2. *QR*: Ketik `'/qr` [spasi] teks Anda' (pastikan didalam tanda petik).\n"
            "3. *AI*: Ketik pesan apapun tanpa awalan garis miring.\n\n"
            "Jika ada kendala, hubungi admin."
        )

    # Mengubah pesan menu utama menjadi teks bantuan sesuai tombol yang diklik
    await query.edit_message_text(text=teks, parse_mode="Markdown")