import logging

def setup_logger() -> logging.Logger:
    """Mengonfigurasi dan mengembalikan instance logger."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )
    # Mengurangi noise log dari library bawaan
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    
    return logging.getLogger("BotUniversal")