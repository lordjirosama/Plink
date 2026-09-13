from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import (
    add_user, is_banned, get_file, get_batch,
    increment_download, get_all_admins
)
from config import OWNER_ID, START_IMAGE, STORAGE_CHANNEL
import asyncio


START_TEXT = """
ʜᴇʟʟᴏ {name} 👋

ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ғɪʟᴇ sʜᴀʀᴇ ʙᴏᴛ 🗂

ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ғɪʟᴇ sʜᴀʀɪɴɢ sᴏʟᴜᴛɪᴏɴ.

• sɪɴɢʟᴇ ғɪʟᴇ ʟɪɴᴋs
• ᴘᴏsᴛᴇʀ + ʟɪɴᴋ sʏsᴛᴇᴍ
• ʙᴀᴛᴄʜ ғɪʟᴇ ʟɪɴᴋs
• sᴇᴄᴜʀᴇ & ғᴀsᴛ
"""

HELP_TEXT = """
📋 ᴄᴏᴍᴍᴀɴᴅs ʟɪsᴛ

/start     — Check bot status
/glink     — Generate single file link
/plink     — Create poster + link
/batch     — Create multi-file batch link
/help      — Show this help
/status    — Bot statistics
/admins    — View admin list
/admin     — Add new admin
/broadcast — Broadcast message
/shortener — Manage URL shorteners
/ban       — Ban a user
/unban     — Unban a user
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.username, user.full_name)

    if await is_banned(user.id):
        await update.message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.")
        return

    args = context.args
    if args:
        param = args[0]
        # Batch link
        if param.startswith("batch_"):
            batch_id = param[6:]
            await send_batch(update, context, batch_id)
            return
        # Single file link
        else:
            await send_file(update, context, param)
            return

    keyboard = [
        [InlineKeyboardButton("📁 ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ", callback_data="help_glink"),
         InlineKeyboardButton("📦 ʙᴀᴛᴄʜ ʟɪɴᴋ", callback_data="help_batch")],
        [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="show_help"),
         InlineKeyboardButton("📊 sᴛᴀᴛᴜs", callback_data="show_status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = START_TEXT.format(name=user.first_name)

    if START_IMAGE:
        await update.message.reply_photo(
            photo=START_IMAGE,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_uid: str):
    file_doc = await get_file(file_uid)
    if not file_doc:
        await update.message.reply_text("❌ ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ.")
        return

    try:
        msg = await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=file_doc["msg_id"]
        )
        await increment_download(file_uid)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ ʀᴇᴛʀɪᴇᴠɪɴɢ ғɪʟᴇ: {str(e)[:100]}")


async def send_batch(update: Update, context: ContextTypes.DEFAULT_TYPE, batch_id: str):
    batch = await get_batch(batch_id)
    if not batch:
        await update.message.reply_text("❌ ʙᴀᴛᴄʜ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return

    await update.message.reply_text(
        f"📦 sᴇɴᴅɪɴɢ {len(batch['file_uids'])} ғɪʟᴇ(s)..."
    )

    success = 0
    for uid in batch["file_uids"]:
        file_doc = await get_file(uid)
        if file_doc:
            try:
                await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=STORAGE_CHANNEL,
                    message_id=file_doc["msg_id"]
                )
                await increment_download(uid)
                success += 1
                await asyncio.sleep(0.5)  # Flood protection
            except Exception:
                pass

    await update.message.reply_text(
        f"✅ {success}/{len(batch['file_uids'])} ғɪʟᴇs sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ."
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🏠 ʙᴀᴄᴋ", callback_data="back_start")]]
    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "show_help":
        await query.edit_message_text(HELP_TEXT)
    elif data == "back_start":
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("📁 ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ", callback_data="help_glink"),
             InlineKeyboardButton("📦 ʙᴀᴛᴄʜ ʟɪɴᴋ", callback_data="help_batch")],
            [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="show_help"),
             InlineKeyboardButton("📊 sᴛᴀᴛᴜs", callback_data="show_status")],
        ]
        await query.edit_message_text(
            START_TEXT.format(name=user.first_name),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
