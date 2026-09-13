from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import (
    add_shortener, get_all_shorteners, get_shortener,
    update_shortener, delete_shortener, toggle_shortener, is_admin
)
from config import OWNER_ID

# States
(S_NAME, S_API, S_DOMAIN, S_NOTE, S_DURATION,
 S_EDIT_CHOICE, S_EDIT_VALUE,
 S_DURATION_SELECT) = range(8)

# Temp store
shortener_temp = {}

DURATION_OPTIONS = [
    ("1 ʜᴏᴜʀ", 1),
    ("6 ʜᴏᴜʀs", 6),
    ("12 ʜᴏᴜʀs", 12),
    ("24 ʜᴏᴜʀs", 24),
    ("48 ʜᴏᴜʀs", 48),
    ("7 ᴅᴀʏs", 168),
    ("ᴘᴇʀᴍᴀɴᴇɴᴛ", 999999),
]

HOW_TO_TEXT = """
❓ ʜᴏᴡ ᴛᴏ sᴇᴛᴜᴘ sʜᴏʀᴛᴇɴᴇʀ

1️⃣ ɢᴏ ᴛᴏ ᴀ sᴜᴘᴘᴏʀᴛᴇᴅ sʜᴏʀᴛᴇɴᴇʀ (ᴇ.ɢ. shrinkme.io, adfly.com)
2️⃣ ᴄʀᴇᴀᴛᴇ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴀɴᴅ ʟᴏɢɪɴ
3️⃣ ɢᴏ ᴛᴏ ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ → ᴀᴘɪ sᴇᴄᴛɪᴏɴ
4️⃣ ᴄᴏᴘʏ ʏᴏᴜʀ ᴀᴘɪ ᴋᴇʏ
5️⃣ ᴜsᴇ /shortener → ➕ ᴀᴅᴅ sʜᴏʀᴛᴇɴᴇʀ
6️⃣ ᴇɴᴛᴇʀ ɴᴀᴍᴇ, ᴀᴘɪ ᴋᴇʏ, ᴅᴏᴍᴀɪɴ
7️⃣ sᴇᴛ ᴀᴄᴄᴇss ᴅᴜʀᴀᴛɪᴏɴ

ɴᴏᴛᴇ: API format — https://{domain}/api?api={key}&url={url}
sᴛᴀɴᴅᴀʀᴅ sʜʀɪɴᴋ-sᴛʏʟᴇ ᴀᴘɪ sᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴅᴇғᴀᴜʟᴛ.
"""


def shortener_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ sʜᴏʀᴛᴇɴᴇʀ", callback_data="sh_add")],
        [InlineKeyboardButton("📋 sʜᴏʀᴛᴇɴᴇʀ ʟɪsᴛ", callback_data="sh_list")],
        [InlineKeyboardButton("❓ ʜᴏᴡ ᴛᴏ sᴇᴛᴜᴘ", callback_data="sh_howto")],
    ])


async def shortener_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ.")
        return

    await update.message.reply_text(
        "⚙️ sʜᴏʀᴛᴇɴᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ",
        reply_markup=shortener_panel_keyboard()
    )


async def shortener_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "sh_add":
        shortener_temp[user_id] = {}
        await query.edit_message_text(
            "➕ ᴀᴅᴅ sʜᴏʀᴛᴇɴᴇʀ\n\n"
            "sᴛᴇᴘ 1/4: sᴇɴᴅ ᴛʜᴇ **ɴᴀᴍᴇ** ᴏғ ᴛʜᴇ sʜᴏʀᴛᴇɴᴇʀ\n"
            "(ᴇ.ɢ. ShrinkMe)",
            parse_mode="Markdown"
        )
        return S_NAME

    elif data == "sh_list":
        await show_shortener_list(query)

    elif data == "sh_howto":
        await query.edit_message_text(
            HOW_TO_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="sh_back")]
            ])
        )

    elif data == "sh_back":
        await query.edit_message_text(
            "⚙️ sʜᴏʀᴛᴇɴᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ",
            reply_markup=shortener_panel_keyboard()
        )

    elif data.startswith("sh_manage_"):
        sid = data.split("sh_manage_")[1]
        await show_manage_panel(query, sid)

    elif data.startswith("sh_toggle_"):
        sid = data.split("sh_toggle_")[1]
        s = await get_shortener(sid)
        if s:
            new_state = not s["enabled"]
            await toggle_shortener(sid, new_state)
            await show_manage_panel(query, sid)

    elif data.startswith("sh_delete_"):
        sid = data.split("sh_delete_")[1]
        await delete_shortener(sid)
        await query.edit_message_text(
            "🗑 sʜᴏʀᴛᴇɴᴇʀ ᴅᴇʟᴇᴛᴇᴅ.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="sh_list")]
            ])
        )

    elif data.startswith("sh_dur_"):
        parts = data.split("_")
        sid = parts[2]
        hours = int(parts[3])
        await update_shortener(sid, {"duration_hours": hours})
        await show_manage_panel(query, sid)


async def show_shortener_list(query):
    shorteners = await get_all_shorteners()
    if not shorteners:
        await query.edit_message_text(
            "📋 ɴᴏ sʜᴏʀᴛᴇɴᴇʀs ᴀᴅᴅᴇᴅ ʏᴇᴛ.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ ᴀᴅᴅ ᴏɴᴇ", callback_data="sh_add")],
                [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="sh_back")],
            ])
        )
        return

    buttons = []
    for s in shorteners:
        status = "🟢" if s["enabled"] else "🔴"
        buttons.append([
            InlineKeyboardButton(
                f"{status} {s['name']} ({s['domain']})",
                callback_data=f"sh_manage_{s['shortener_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="sh_back")])

    await query.edit_message_text(
        "📋 sʜᴏʀᴛᴇɴᴇʀ ʟɪsᴛ",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_manage_panel(query, sid: str):
    s = await get_shortener(sid)
    if not s:
        await query.edit_message_text("❌ sʜᴏʀᴛᴇɴᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return

    status = "🟢 ᴇɴᴀʙʟᴇᴅ" if s["enabled"] else "🔴 ᴅɪsᴀʙʟᴇᴅ"
    toggle_label = "🔴 ᴅɪsᴀʙʟᴇ" if s["enabled"] else "🟢 ᴇɴᴀʙʟᴇ"

    dur_buttons = [
        InlineKeyboardButton(label, callback_data=f"sh_dur_{sid}_{hours}")
        for label, hours in DURATION_OPTIONS
    ]
    dur_rows = [dur_buttons[i:i+3] for i in range(0, len(dur_buttons), 3)]

    keyboard = [
        [InlineKeyboardButton(toggle_label, callback_data=f"sh_toggle_{sid}"),
         InlineKeyboardButton("🗑 ᴅᴇʟᴇᴛᴇ", callback_data=f"sh_delete_{sid}")],
        *dur_rows,
        [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="sh_list")],
    ]

    await query.edit_message_text(
        f"⚙️ ᴍᴀɴᴀɢᴇ: **{s['name']}**\n\n"
        f"🌐 ᴅᴏᴍᴀɪɴ: `{s['domain']}`\n"
        f"⏱ ᴅᴜʀᴀᴛɪᴏɴ: `{s['duration_hours']}h`\n"
        f"sᴛᴀᴛᴜs: {status}\n\n"
        f"sᴇʟᴇᴄᴛ ɴᴇᴡ ᴅᴜʀᴀᴛɪᴏɴ ᴏʀ ᴛᴏɢɢʟᴇ:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ─── Conversation for adding shortener ──────────────────
async def sh_receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    shortener_temp.setdefault(user_id, {})["name"] = update.message.text
    await update.message.reply_text(
        "sᴛᴇᴘ 2/4: sᴇɴᴅ ᴛʜᴇ **ᴀᴘɪ ᴋᴇʏ**",
        parse_mode="Markdown"
    )
    return S_API


async def sh_receive_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    shortener_temp[user_id]["api_key"] = update.message.text
    await update.message.reply_text(
        "sᴛᴇᴘ 3/4: sᴇɴᴅ ᴛʜᴇ **ᴅᴏᴍᴀɪɴ** (e.g. `shrinkme.io`)",
        parse_mode="Markdown"
    )
    return S_DOMAIN


async def sh_receive_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    shortener_temp[user_id]["domain"] = update.message.text.strip()
    await update.message.reply_text(
        "sᴛᴇᴘ 4/4: sᴇɴᴅ ᴀ **ɴᴏᴛᴇ** (ᴏᴘᴛɪᴏɴᴀʟ) ᴏʀ sᴇɴᴅ `-` ᴛᴏ sᴋɪᴘ",
        parse_mode="Markdown"
    )
    return S_NOTE


async def sh_receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    note = update.message.text
    shortener_temp[user_id]["note"] = "" if note == "-" else note

    buttons = [[InlineKeyboardButton(label, callback_data=f"shdur_{hours}")]
               for label, hours in DURATION_OPTIONS]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

    await update.message.reply_text(
        "sᴇʟᴇᴄᴛ ᴀᴄᴄᴇss ᴅᴜʀᴀᴛɪᴏɴ:",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return S_DURATION


async def sh_receive_duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    hours = int(query.data.split("shdur_")[1])
    data = shortener_temp.pop(user_id, {})
    data["duration_hours"] = hours

    sid = await add_shortener(
        name=data.get("name", "Unknown"),
        api_key=data.get("api_key", ""),
        domain=data.get("domain", ""),
        note=data.get("note", ""),
        duration_hours=hours
    )

    await query.edit_message_text(
        f"✅ sʜᴏʀᴛᴇɴᴇʀ ᴀᴅᴅᴇᴅ!\n\n"
        f"📛 ɴᴀᴍᴇ: **{data.get('name')}**\n"
        f"🌐 ᴅᴏᴍᴀɪɴ: `{data.get('domain')}`\n"
        f"⏱ ᴅᴜʀᴀᴛɪᴏɴ: `{hours}h`",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def sh_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shortener_temp.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    return ConversationHandler.END
