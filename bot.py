from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import edge_tts
import os

TOKEN = "8820429331:AAGALjWhVq-mJBsg7VpPgIxsQ9jy0scBldg"

VOICE = "ru-RU-DmitryNeural"

async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Send text like this:\n/tts Привет друзья"
        )
        return

    filename = "voice.mp3"

    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filename)

        with open(filename, "rb") as audio:
            await update.message.reply_voice(audio)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("tts", tts))

print("Bot is running...")

app.run_polling()
