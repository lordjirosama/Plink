from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import create_batch, add_file_to_batch, store_file, is_admin, get_batch
from utils.helpers import get_batch_link, human_size
from config import OWNER_ID, STORAGE_CHANNEL
from handlers.files import _extract_file_info

# States
BATCH_COLLECTING = 1

# Temp active batches per admin
active_batches = {}


async def batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_admin(user_id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return ConversationHandler.END

    batch_id = await create_batch(admin_id=user_id)
    active_batches[user_id] = {"batch_id": batch_id, "count": 0}

    keyboard = [[InlineKeyboardButton("✅ ᴅᴏɴᴇ — ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ", callback_data=f"batch_done_{batch_id}")]]

    await update.message.reply_text(
        f"📦 ʙᴀᴛᴄʜ sᴛᴀʀᴛᴇᴅ!\n\n"
        f"ɴᴏᴡ sᴇɴᴅ ᴀʟʟ ғɪʟᴇs ᴏɴᴇ ʙʏ ᴏɴᴇ.\n"
        f"ᴡʜᴇɴ ᴅᴏɴᴇ, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴏʀ sᴇɴᴅ /batchdone\n\n"
        f"sᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return BATCH_COLLECTING


async def batch_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id

    if user_id not in active_batches:
        return BATCH_COLLECTING

    file_info = _extract_file_info(msg)
    if not file_info:
        await msg.reply_text("❌ ɪɴᴠᴀʟɪᴅ ғɪʟᴇ, sᴋɪᴘᴘɪɴɢ.")
        return BATCH_COLLECTING

    tg_file_id, file_name, file_size, file_type = file_info
    batch_id = active_batches[user_id]["batch_id"]

    try:
        stored_msg = await msg.forward(STORAGE_CHANNEL)
    except Exception as e:
        await msg.reply_text(f"❌ sᴛᴏʀᴀɢᴇ ᴇʀʀᴏʀ: {str(e)[:80]}")
        return BATCH_COLLECTING

    file_uid = await store_file(
        tg_file_id=tg_file_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        uploader_id=user_id,
        msg_id=stored_msg.message_id,
        batch_id=batch_id
    )
    await add_file_to_batch(batch_id, file_uid)

    active_batches[user_id]["count"] += 1
    count = active_batches[user_id]["count"]

    await msg.reply_text(
        f"✅ ғɪʟᴇ {count} ᴀᴅᴅᴇᴅ: **{file_name}** ({human_size(file_size)})\n"
        f"sᴇɴᴅ ᴍᴏʀᴇ ᴏʀ /batchdone ᴛᴏ ғɪɴɪsʜ.",
        parse_mode="Markdown"
    )
    return BATCH_COLLECTING


async def batch_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in active_batches:
        await update.message.reply_text("❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ʙᴀᴛᴄʜ.")
        return ConversationHandler.END

    batch_data = active_batches.pop(user_id)
    batch_id = batch_data["batch_id"]
    count = batch_data["count"]

    if count == 0:
        await update.message.reply_text("❌ ɴᴏ ғɪʟᴇs ᴀᴅᴅᴇᴅ ᴛᴏ ʙᴀᴛᴄʜ.")
        return ConversationHandler.END

    link = get_batch_link(batch_id)

    keyboard = [[InlineKeyboardButton("📥 ᴏᴘᴇɴ ʙᴀᴛᴄʜ", url=link)]]

    await update.message.reply_text(
        f"📦 ʙᴀᴛᴄʜ ʀᴇᴀᴅʏ!\n\n"
        f"📁 ᴛᴏᴛᴀʟ ғɪʟᴇs: **{count}**\n"
        f"🔗 `{link}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def batch_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in active_batches:
        await query.edit_message_text("❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ʙᴀᴛᴄʜ.")
        return ConversationHandler.END

    batch_data = active_batches.pop(user_id)
    batch_id = batch_data["batch_id"]
    count = batch_data["count"]

    if count == 0:
        await query.edit_message_text("❌ ɴᴏ ғɪʟᴇs ᴀᴅᴅᴇᴅ.")
        return ConversationHandler.END

    link = get_batch_link(batch_id)
    keyboard = [[InlineKeyboardButton("📥 ᴏᴘᴇɴ ʙᴀᴛᴄʜ", url=link)]]

    await query.edit_message_text(
        f"📦 ʙᴀᴛᴄʜ ʀᴇᴀᴅʏ!\n\n"
        f"📁 ᴛᴏᴛᴀʟ ғɪʟᴇs: **{count}**\n"
        f"🔗 `{link}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def batch_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_batches.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ ʙᴀᴛᴄʜ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    return ConversationHandler.END
