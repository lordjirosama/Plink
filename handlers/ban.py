from telegram import Update
from telegram.ext import ContextTypes
from database.db import ban_user, unban_user, is_admin, get_all_banned
from utils.helpers import is_valid_user_id
from config import OWNER_ID


async def ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ ᴜsᴀɢᴇ: `/ban <user_id> [reason]`",
            parse_mode="Markdown"
        )
        return

    target_id = context.args[0]
    if not is_valid_user_id(target_id):
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
        return

    target_id = int(target_id)
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"

    if target_id == OWNER_ID:
        await update.message.reply_text("❌ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴏᴡɴᴇʀ.")
        return

    banned = await ban_user(target_id, reason)
    if banned:
        await update.message.reply_text(
            f"🚫 ᴜsᴇʀ `{target_id}` ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.\n"
            f"📝 ʀᴇᴀsᴏɴ: {reason}",
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"🚫 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.\n📝 ʀᴇᴀsᴏɴ: {reason}"
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(f"ℹ️ ᴜsᴇʀ `{target_id}` ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.", parse_mode="Markdown")


async def unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ ᴜsᴀɢᴇ: `/unban <user_id>`",
            parse_mode="Markdown"
        )
        return

    target_id = context.args[0]
    if not is_valid_user_id(target_id):
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
        return

    unbanned = await unban_user(int(target_id))
    if unbanned:
        await update.message.reply_text(
            f"✅ ᴜsᴇʀ `{target_id}` ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.",
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=int(target_id),
                text="✅ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ. ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ."
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(f"❌ ᴜsᴇʀ `{target_id}` ᴡᴀs ɴᴏᴛ ʙᴀɴɴᴇᴅ.", parse_mode="Markdown")


async def banned_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    banned = await get_all_banned()
    if not banned:
        await update.message.reply_text("✅ ɴᴏ ʙᴀɴɴᴇᴅ ᴜsᴇʀs.")
        return

    lines = ["🚫 ʙᴀɴɴᴇᴅ ᴜsᴇʀs\n"]
    for i, b in enumerate(banned, 1):
        lines.append(f"{i}. `{b['user_id']}` — {b.get('reason', 'No reason')}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
