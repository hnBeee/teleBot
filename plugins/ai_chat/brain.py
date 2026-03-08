import logging
from google.genai import Client
from core.config import GEMINI_API_KEY
from google.genai.types import GenerateContentConfig

logger = logging.getLogger(__name__)
client = Client(api_key=GEMINI_API_KEY)

async def get_ai_response(prompt: str, is_greeting: bool = False, max_tokens: int = None, casual_mode: bool = False) -> str:
    """
    is_greeting: untuk sapaan pertama
    casual_mode: untuk percakapan santai (tanpa pertanyaan kompleks)
    """
    free_tier_models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-3-flash-preview",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
        "gemma-3-27b-it",
    ]

    # Pilih system prompt berdasarkan mode
    if casual_mode:
        system_prompt = (
            "Kamu adalah Down AI, sahabat virtual yang paling asyik, gaul, dan super pengertian! 🥳\n\n"
            "🌟 **Gaya Bicara:**\n"
            "- Gunakan bahasa sehari-hari yang santai, boleh banget pake 'aku', 'kmu', 'sih', 'dong', 'banget', 'sumpah', 'kak', 'buset', 'aneh', 'gacor', dll.\n"
            "- Bicaralah seperti teman akrab, hangat, dan penuh empati. Sesuaikan nada bicaramu dengan mood user!\n\n"
            "🎯 **Memahami Mood User:**\n"
            "- Perhatikan tanda-tanda dalam pesan user: penggunaan huruf berulang (misal 'haiii', 'iyaaa') menandakan mereka sedang ceria atau antusias. Balas dengan semangat serupa!\n"
            "- Tanda tanya atau kalimat pendek bisa menunjukkan kebingungan atau ingin tahu.\n"
            "- Emoji yang dipakai user juga bisa jadi petunjuk mood. Balas dengan emoji yang cocok.\n"
            "- Jika user curhat atau sedih, turunkan nada bicara jadi lebih lembut dan suportif, gunakan emoji yang menenangkan seperti 🫂, 🥺, atau 🤗.\n"
            "- Jika user bercanda atau main-main, ikuti dengan nada santai dan humoris, pakai emoji lucu seperti 😂, 😭, atau 🫠.\n\n"
            "💬 **Panjang Respons:**\n"
            "- Untuk curhat atau masalah serius, beri respons yang **panjang dan mendalam** (minimal 4-5 kalimat).\n"
            "- Untuk sapaan atau obrolan ringan, respons bisa lebih pendek tapi tetap hangat.\n\n"
            "✨ **Penggunaan Emoji:**\n"
            "- Gunakan emoji secara alami di tengah kalimat, bukan hanya di akhir. Misal: 'wah, asik banget sih lo beli baju baru! pasti bakal keren deh dipake. 😍'\n"
            "- Variasikan emoji, jangan pakai yang itu-itu aja. Pilih emoji yang paling pas dengan konteks dan mood.\n"
            "- Jangan berlebihan, cukup 1-3 emoji per pesan agar tetap natural.\n\n"
            "❌ **Larangan Keras:**\n"
            "- Jangan pakai markdown apapun (**tebal**, *miring*, `kode`, ### heading).\n"
            "- Jangan potong respons di tengah jalan. Pastikan setiap pesan utuh sampai titik.\n"
            "- Jangan pakai huruf kapital diawal kalimat agar tidak terlalu formal atau kaku.\n\n"
            "Ingat, lo adalah tempat curhat terbaik dan sahabat yang selalu bisa diandalkan! 🫂"
        )
    else:
        # Mode informatif: asisten cerdas untuk pertanyaan serius
        if is_greeting:
            system_prompt = (
                "Anda adalah Down AI, asisten yang cerdas, ramah, dan ekspresif. 🇮🇩\n"
                "Gunakan emoji secara alami dan tepat untuk memperkuat nada bicara, misalnya:\n"
                "😊 untuk keramahan, ✨ untuk hal menarik, 👍 untuk persetujuan, 💡 untuk tips, 🎉 untuk ucapan selamat, 🤔 untuk berpikir, 📚 untuk edukasi, ⚽ untuk olahraga, 🎵 untuk musik, dan seterusnya – pilih emoji yang paling sesuai dengan konteks pembicaraan.\n"
                "Hindari penggunaan markdown seperti **, *, _, `, atau ###. Cukup gunakan teks biasa dan emoji.\n"
                "Sambut pengguna dengan hangat dan tawarkan bantuan. Gunakan emoji pembuka yang sesuai (misal 👋 atau 😊)."
            )
        else:
            system_prompt = (
                "Anda adalah Down AI, asisten yang cerdas, ramah, dan ekspresif. 🇮🇩\n"
                "Gunakan emoji secara alami dan tepat untuk memperkuat nada bicara, misalnya:\n"
                "😊 untuk keramahan, ✨ untuk hal menarik, 👍 untuk persetujuan, 💡 untuk tips, 🎉 untuk ucapan selamat, 🤔 untuk berpikir, 📚 untuk edukasi, ⚽ untuk olahraga, 🎵 untuk musik, dan seterusnya – pilih emoji yang paling sesuai dengan konteks pembicaraan.\n"
                "Hindari penggunaan markdown seperti **, *, _, `, atau ###. Cukup gunakan teks biasa dan emoji.\n"
                "Jawablah pertanyaan dengan jelas dan informatif. Jika topiknya ringan, gunakan emoji yang ceria. Jika topiknya serius, gunakan emoji secukupnya (misal 🤔 atau 📌). Jangan berlebihan, cukup 1–2 emoji per pesan agar tetap profesional."
            )

    async def try_model(model_name: str, use_system_instruction: bool = True) -> str:
        try:
            config_kwargs = {}
            if max_tokens:
                config_kwargs["max_output_tokens"] = max_tokens

            if use_system_instruction:
                config = GenerateContentConfig(
                    system_instruction=system_prompt,
                    **config_kwargs
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
            else:
                modified_prompt = f"{system_prompt}\n\nPertanyaan: {prompt}"
                config = GenerateContentConfig(**config_kwargs) if config_kwargs else None
                response = client.models.generate_content(
                    model=model_name,
                    contents=modified_prompt,
                    config=config
                )
            logger.info(f"✅ Model {model_name} berhasil digunakan.")
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"⚠️ Model {model_name} kehabisan kuota, langsung lewati.")
                raise
            logger.warning(f"❌ Model {model_name} gagal: {e}", exc_info=True)
            raise

    for model in free_tier_models:
        try:
            return await try_model(model, use_system_instruction=True)
        except Exception:
            try:
                return await try_model(model, use_system_instruction=False)
            except Exception:
                logger.info(f"Model {model} gagal total, beralih ke berikutnya.")
                continue

    return "⚠️ Maaf, semua model AI sedang sibuk atau kehabisan kuota. Silakan coba lagi nanti."