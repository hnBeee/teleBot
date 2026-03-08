import qrcode
import os
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

def generate_qr_code(data: str) -> str:
    """Membuat QR Code asli dan menyimpan sebagai file PNG."""
    try:
        # Buat folder 'temp' jika belum ada untuk menyimpan file sementara
        if not os.path.exists("temp"):
            os.makedirs("temp")
            
        filename = f"temp/qr_{uuid4().hex[:8]}.png"
        filepath = os.path.abspath(filename)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        
        return filepath
    except Exception as e:
        logger.error(f"Gagal generate QR: {e}")
        raise e