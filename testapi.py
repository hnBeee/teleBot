import asyncio
from google.genai import Client
from core.config import GEMINI_API_KEY

async def cek_model():
    client = Client(api_key=GEMINI_API_KEY)
    print("Model yang mendukung 'generateContent':")
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            print(f"- {m.name} ({m.display_name})")

asyncio.run(cek_model())