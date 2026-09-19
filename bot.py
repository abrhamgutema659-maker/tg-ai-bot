import os
import logging
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

HF_URL = "https://router.huggingface.co/fal-ai/fal-ai/flux/schnell"


async def generate_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()

    if not prompt:
        return

    await update.message.reply_text(
        "🎨 ፎቶውን እየፈጠርኩ ነው... ⏳"
    )

    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            HF_URL,
            headers=headers,
            json={"prompt": prompt},
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        image_url = data["images"][0]["url"]

        await update.message.reply_photo(
            photo=image_url,
            caption="✨ የእርስዎ ፎቶ",
        )

    except Exception as e:
        logging.exception("Image generation error")
        await update.message.reply_text(
            f"❌ ፎቶ ማመንጨት አልተቻለም።\n\n{str(e)[:500]}"
        )


def main():
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30)
        .read_timeout(60)
        .write_timeout(60)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            generate_photo,
        )
    )

    print("🤖 Photo Generator Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
