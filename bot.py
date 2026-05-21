from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import edge_tts
import os

TOKEN = os.environ.get("8820429331:AAGALjWhVq-mJBsg7VpPgIxsQ9jy0scBldg")

# Available voices
VOICES = {
    "ru": {
        "male": {"Dmitry": "ru-RU-DmitryNeural"},
        "female": {"Svetlana": "ru-RU-SvetlanaNeural"}
    },
    "en": {
        "male": {"Guy": "en-US-GuyNeural", "Eric": "en-US-EricNeural"},
        "female": {"Jenny": "en-US-JennyNeural", "Aria": "en-US-AriaNeural"}
    },
    "de": {
        "male": {"Conrad": "de-DE-ConradNeural"},
        "female": {"Katja": "de-DE-KatjaNeural"}
    },
    "fr": {
        "male": {"Henri": "fr-FR-HenriNeural"},
        "female": {"Denise": "fr-FR-DeniseNeural"}
    },
    "es": {
        "male": {"Alvaro": "es-ES-AlvaroNeural"},
        "female": {"Elvira": "es-ES-ElviraNeural"}
    },
    "zh": {
        "male": {"Yunxi": "zh-CN-YunxiNeural"},
        "female": {"Xiaoxiao": "zh-CN-XiaoxiaoNeural"}
    },
}

LANG_NAMES = {"ru": "🇷🇺 Russian", "en": "🇺🇸 English", "de": "🇩🇪 German",
              "fr": "🇫🇷 French", "es": "🇪🇸 Spanish", "zh": "🇨🇳 Chinese"}

SPEED_OPTIONS = {
    "slow": "-20%",
    "normal": "+0%",
    "fast": "+25%",
    "very fast": "+50%"
}

# Default user settings
user_settings = {}

def get_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "lang": "ru",
            "gender": "male",
            "voice": "Dmitry",
            "speed": "normal"
        }
    return user_settings[user_id]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 *TTS Bot*\n\n"
        "/tts <text> — Convert text to speech\n"
        "/settings — Change voice, language, speed\n"
        "/voices — See all available voices",
        parse_mode="Markdown"
    )

# /tts
async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /tts Привет друзья")
        return

    s = get_settings(update.effective_user.id)
    voice_name = VOICES[s["lang"]][s["gender"]][s["voice"]]
    rate = SPEED_OPTIONS[s["speed"]]
    filename = f"voice_{update.effective_user.id}.mp3"

    try:
        communicate = edge_tts.Communicate(text, voice_name, rate=rate)
        await communicate.save(filename)
        with open(filename, "rb") as audio:
            await update.message.reply_voice(audio, caption=f"🎙 {s['voice']} | {LANG_NAMES[s['lang']]} | {s['speed']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# /voices
async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🎙 *Available Voices*\n\n"
    for lang, code in LANG_NAMES.items():
        msg += f"{code}\n"
        for gender, v in VOICES[lang].items():
            names = ", ".join(v.keys())
            msg += f"  {'👨' if gender == 'male' else '👩'} {names}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# /settings — show language picker
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")]
                for code, name in LANG_NAMES.items()]
    await update.message.reply_text(
        "🌐 Choose language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Callbacks
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    s = get_settings(uid)
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        s["lang"] = lang
        # Pick first available male voice as default
        s["gender"] = "male"
        s["voice"] = list(VOICES[lang]["male"].keys())[0]
        keyboard = [
            [InlineKeyboardButton("👨 Male", callback_data="gender_male"),
             InlineKeyboardButton("👩 Female", callback_data="gender_female")]
        ]
        await query.edit_message_text("Choose gender:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("gender_"):
        gender = data.split("_")[1]
        s["gender"] = gender
        s["voice"] = list(VOICES[s["lang"]][gender].keys())[0]
        voices_list = VOICES[s["lang"]][gender]
        keyboard = [[InlineKeyboardButton(name, callback_data=f"voice_{name}")]
                    for name in voices_list]
        await query.edit_message_text("Choose voice:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("voice_"):
        voice = data.split("_")[1]
        s["voice"] = voice
        keyboard = [[InlineKeyboardButton(sp.capitalize(), callback_data=f"speed_{sp}")]
                    for sp in SPEED_OPTIONS]
        await query.edit_message_text("Choose speed:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("speed_"):
        speed = data.replace("speed_", "")
        s["speed"] = speed
        await query.edit_message_text(
            f"✅ Settings saved!\n\n"
            f"🌐 Language: {LANG_NAMES[s['lang']]}\n"
            f"{'👨' if s['gender'] == 'male' else '👩'} Voice: {s['voice']}\n"
            f"⚡ Speed: {speed}\n\n"
            f"Use /tts <text> to generate speech"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("tts", tts))
app.add_handler(CommandHandler("settings", settings))
app.add_handler(CommandHandler("voices", voices))
app.add_handler(CallbackQueryHandler(callback_handler))

print("Bot is running...")
app.run_polling()
