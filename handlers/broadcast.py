from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_all_users, is_admin, is_banned
from config import OWNER_ID
import asyncio

WAITING_BROADCAST = 1


async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📢 sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.\n\n"
        "sᴜᴘᴘᴏʀᴛᴇᴅ: ᴛᴇxᴛ, ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, ᴅᴏᴄᴜᴍᴇɴᴛ\n\n"
        "sᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
    )
    return WAITING_BROADCAST


async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    users = await get_all_users()

    status_msg = await msg.reply_text(
        f"📢 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ {len(users)} ᴜsᴇʀs...\n⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ."
    )

    success = 0
    failed = 0
    blocked = 0

    for i, user in enumerate(users):
        uid = user["user_id"]

        if await is_banned(uid):
            blocked += 1
            continue

        try:
            await msg.copy(chat_id=uid)
            success += 1
        except Exception as e:
            err = str(e).lower()
            if "blocked" in err or "deactivated" in err:
                blocked += 1
            else:
                failed += 1

        # Flood protection: update progress every 50 users
        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 ᴘʀᴏɢʀᴇss: {i+1}/{len(users)}\n"
                    f"✅ {success} | ❌ {failed} | 🚫 {blocked}"
                )
            except Exception:
                pass
            await asyncio.sleep(1)

        await asyncio.sleep(0.05)  # Avoid hitting Telegram flood limits

    await status_msg.edit_text(
        f"📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ!\n\n"
        f"✅ sᴜᴄᴄᴇss: `{success}`\n"
        f"❌ ғᴀɪʟᴇᴅ: `{failed}`\n"
        f"🚫 sᴋɪᴘᴘᴇᴅ (ʙᴀɴɴᴇᴅ/ʙʟᴏᴄᴋᴇᴅ): `{blocked}`",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    return ConversationHandler.END
