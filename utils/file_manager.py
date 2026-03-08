import os
import logging

def delete_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logging.error(f"Gagal hapus file: {e}")