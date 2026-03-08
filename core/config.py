import os
from dotenv import load_dotenv

# Load variabel dari .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Path ke file cookies (menggunakan path absolut agar aman)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_PATH = os.path.join(BASE_DIR, "cookies.txt")