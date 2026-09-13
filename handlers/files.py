from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import store_file, is_admin
from utils.helpers import get_file_link, human_size
from config import OWNER_ID, STORAGE_CHANNEL

# Conversation states
WAITING_FILE = 1
WAITING_POSTER = 2
WAITING_PLINK_FILE = 3

# Temp store for plink poster
plink_temp = {}


# ─── GLINK ──────────────────────────────────────────────
async def glink_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📁 ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ғɪʟᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ʟɪɴᴋ ғᴏʀ.\n\n"
        "sᴇɴᴅ /cancel ᴛᴏ sᴛᴏᴘ."
    )
    return WAITING_FILE


async def glink_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file_info = _extract_file_info(msg)

    if not file_info:
        await msg.reply_text("❌ ɪɴᴠᴀʟɪᴅ ғɪʟᴇ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ғɪʟᴇ.")
        return WAITING_FILE

    tg_file_id, file_name, file_size, file_type = file_info

    # Forward to storage channel
    try:
        stored_msg = await msg.forward(STORAGE_CHANNEL)
    except Exception as e:
        await msg.reply_text(f"❌ sᴛᴏʀᴀɢᴇ ᴇʀʀᴏʀ: {str(e)[:100]}")
        return ConversationHandler.END

    file_uid = await store_file(
        tg_file_id=tg_file_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        uploader_id=msg.from_user.id,
        msg_id=stored_msg.message_id
    )

    link = get_file_link(file_uid)

    await msg.reply_text(
        f"✅ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ\n\n"
        f"📁 **{file_name}**\n"
        f"📦 sɪᴢᴇ: {human_size(file_size)}\n"
        f"🔗 `{link}`",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ─── PLINK ──────────────────────────────────────────────
async def plink_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return ConversationHandler.END

    await update.message.reply_text(
        "🖼 ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴏʀ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ **ᴘᴏsᴛᴇʀ** (ɪᴍᴀɢᴇ).\n\n"
        "sᴇɴᴅ /cancel ᴛᴏ sᴛᴏᴘ.",
        parse_mode="Markdown"
    )
    return WAITING_POSTER


async def plink_receive_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg.photo and not msg.document:
        await msg.reply_text("❌ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀɴ ɪᴍᴀɢᴇ ᴀs ᴘᴏsᴛᴇʀ.")
        return WAITING_POSTER

    if msg.photo:
        poster_file_id = msg.photo[-1].file_id
    else:
        poster_file_id = msg.document.file_id

    plink_temp[msg.from_user.id] = {"poster": poster_file_id}

    await msg.reply_text(
        "✅ ᴘᴏsᴛᴇʀ ʀᴇᴄᴇɪᴠᴇᴅ!\n\n"
        "📁 ɴᴏᴡ sᴇɴᴅ ᴛʜᴇ **ғɪʟᴇ** ᴛᴏ ᴀᴛᴛᴀᴄʜ ᴡɪᴛʜ ᴛʜɪs ᴘᴏsᴛᴇʀ.",
        parse_mode="Markdown"
    )
    return WAITING_PLINK_FILE


async def plink_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    file_info = _extract_file_info(msg)

    if not file_info:
        await msg.reply_text("❌ ɪɴᴠᴀʟɪᴅ ғɪʟᴇ.")
        return WAITING_PLINK_FILE

    tg_file_id, file_name, file_size, file_type = file_info

    try:
        stored_msg = await msg.forward(STORAGE_CHANNEL)
    except Exception as e:
        await msg.reply_text(f"❌ sᴛᴏʀᴀɢᴇ ᴇʀʀᴏʀ: {str(e)[:100]}")
        return ConversationHandler.END

    file_uid = await store_file(
        tg_file_id=tg_file_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        uploader_id=user_id,
        msg_id=stored_msg.message_id
    )

    link = get_file_link(file_uid)
    poster = plink_temp.pop(user_id, {}).get("poster")

    caption = (
        f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ 🔗\n\n"
        f"📁 **{file_name}**\n"
        f"📦 {human_size(file_size)}\n\n"
        f"`{link}`"
    )

    keyboard = [[InlineKeyboardButton("📥 ɢᴇᴛ ғɪʟᴇ", url=link)]]

    if poster:
        await msg.reply_photo(
            photo=poster,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await msg.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plink_temp.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    return ConversationHandler.END


# ─── HELPER ─────────────────────────────────────────────
def _extract_file_info(msg):
    if msg.document:
        f = msg.document
        return f.file_id, f.file_name or "document", f.file_size or 0, "document"
    elif msg.video:
        f = msg.video
        return f.file_id, f.file_name or "video.mp4", f.file_size or 0, "video"
    elif msg.audio:
        f = msg.audio
        return f.file_id, f.file_name or "audio.mp3", f.file_size or 0, "audio"
    elif msg.photo:
        f = msg.photo[-1]
        return f.file_id, "photo.jpg", f.file_size or 0, "photo"
    elif msg.voice:
        f = msg.voice
        return f.file_id, "voice.ogg", f.file_size or 0, "voice"
    elif msg.video_note:
        f = msg.video_note
        return f.file_id, "video_note.mp4", f.file_size or 0, "video_note"
    return None
