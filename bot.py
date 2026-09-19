import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN,
    timeout=180,
)


async def generate_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()

    if not prompt:
        return

    await update.message.reply_text(
        "🎨 ፎቶውን እየፈጠርኩ ነው... ⏳"
    )

    try:
        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        image_path = "/tmp/generated_image.png"
        image.save(image_path)

        await update.message.reply_photo(
            photo=open(image_path, "rb"),
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
