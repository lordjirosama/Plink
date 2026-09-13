from telegram import Update
from telegram.ext import ContextTypes
from database.db import (
    add_admin, remove_admin, get_all_admins, is_admin,
    total_users, total_files, total_batches, total_admins, total_banned
)
from utils.helpers import is_valid_user_id
from config import OWNER_ID
import time

START_TIME = time.time()


def get_uptime() -> str:
    seconds = int(time.time() - START_TIME)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    return f"{days}d {hours}h {mins}m {secs}s"


async def add_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ ᴏᴡɴᴇʀ ᴏɴʟʏ.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ ᴜsᴀɢᴇ: `/admin <user_id>`",
            parse_mode="Markdown"
        )
        return

    target_id = context.args[0]
    if not is_valid_user_id(target_id):
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
        return

    target_id = int(target_id)
    if target_id == OWNER_ID:
        await update.message.reply_text("ℹ️ ᴏᴡɴᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ sᴜᴘᴇʀ ᴀᴅᴍɪɴ.")
        return

    added = await add_admin(target_id)
    if added:
        await update.message.reply_text(f"✅ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ: `{target_id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"ℹ️ `{target_id}` ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ.", parse_mode="Markdown")


async def del_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ ᴏᴡɴᴇʀ ᴏɴʟʏ.")
        return

    if not context.args:
        await update.message.reply_text("ℹ️ ᴜsᴀɢᴇ: `/deladmin <user_id>`", parse_mode="Markdown")
        return

    target_id = context.args[0]
    if not is_valid_user_id(target_id):
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
        return

    removed = await remove_admin(int(target_id))
    if removed:
        await update.message.reply_text(f"✅ ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ: `{target_id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{target_id}` ᴡᴀs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.", parse_mode="Markdown")


async def list_admins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    admins = await get_all_admins()

    lines = [f"👑 ᴀᴅᴍɪɴ ʟɪsᴛ\n"]
    lines.append(f"👑 ᴏᴡɴᴇʀ: `{OWNER_ID}`")

    if admins:
        for i, a in enumerate(admins, 1):
            lines.append(f"🔹 {i}. `{a['user_id']}`")
    else:
        lines.append("ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴀᴅᴍɪɴs.")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    users = await total_users()
    files = await total_files()
    batches = await total_batches()
    admins = await total_admins()
    banned = await total_banned()
    uptime = get_uptime()

    text = (
        f"ʙᴏᴛ sᴛᴀᴛᴜs 📊\n\n"
        f"👥 ᴜsᴇʀs: `{users}`\n"
        f"📁 ғɪʟᴇs: `{files}`\n"
        f"📦 ʙᴀᴛᴄʜᴇs: `{batches}`\n"
        f"👑 ᴀᴅᴍɪɴs: `{admins + 1}`\n"
        f"🚫 ʙᴀɴɴᴇᴅ: `{banned}`\n"
        f"⏱ ᴜᴘᴛɪᴍᴇ: `{uptime}`\n"
        f"🟢 sᴛᴀᴛᴜs: ᴏɴʟɪɴᴇ"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
