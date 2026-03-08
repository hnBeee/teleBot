import os
import logging
from yt_dlp import YoutubeDL
from core.config import COOKIES_PATH

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = 'temp'
MAX_FILE_SIZE = 50 * 1024 * 1024  # Batas 50MB Telegram

def get_ytdlp_options(mode: str) -> dict:
    """Konfigurasi yt-dlp berdasarkan pilihan resolusi."""
    opts = {
        'noplaylist': True,
        'quiet': True,
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
    }

    if os.path.exists(COOKIES_PATH):
        opts['cookiefile'] = COOKIES_PATH

    # Logika pemilihan format sesuai file downloader.py Anda
    if mode == 'dl_best':
        opts['format'] = 'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif mode == 'dl_720':
        opts['format'] = 'bestvideo[height<=720][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif mode == 'dl_480':
        opts['format'] = 'bestvideo[height<=480][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif mode == 'dl_mp3':
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    return opts

def execute_ytdlp(url: str, mode: str) -> dict:
    """Proses download di background thread."""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    opts = get_ytdlp_options(mode)
    
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            if mode == 'dl_mp3':
                # Sesuaikan ekstensi jika mode MP3
                file_path = os.path.splitext(file_path)[0] + '.mp3'
                
            return {'path': file_path, 'error': None, 'title': info.get('title', 'Video')}
    except Exception as e:
        logger.error(f"Error yt-dlp: {e}")
        return {'path': None, 'error': str(e)}