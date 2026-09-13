from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)
from config import BOT_TOKEN

from handlers.start import start_handler, help_handler, callback_handler
from handlers.files import (
    glink_start, glink_receive_file,
    plink_start, plink_receive_poster, plink_receive_file,
    cancel_handler, WAITING_FILE, WAITING_POSTER, WAITING_PLINK_FILE
)
from handlers.batch import (
    batch_start, batch_receive_file, batch_done,
    batch_cancel, batch_done_callback, BATCH_COLLECTING
)
from handlers.admin import (
    add_admin_handler, del_admin_handler,
    list_admins_handler, status_handler
)
from handlers.broadcast import (
    broadcast_start, broadcast_send, broadcast_cancel, WAITING_BROADCAST
)
from handlers.ban import ban_handler, unban_handler, banned_list_handler
from handlers.shortener import (
    shortener_menu, shortener_callback,
    sh_receive_name, sh_receive_api, sh_receive_domain,
    sh_receive_note, sh_receive_duration_callback, sh_cancel,
    S_NAME, S_API, S_DOMAIN, S_NOTE, S_DURATION
)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ─── glink conversation ───────────────────────────
    glink_conv = ConversationHandler(
        entry_points=[CommandHandler("glink", glink_start)],
        states={WAITING_FILE: [MessageHandler(filters.ALL & ~filters.COMMAND, glink_receive_file)]},
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    # ─── plink conversation ───────────────────────────
    plink_conv = ConversationHandler(
        entry_points=[CommandHandler("plink", plink_start)],
        states={
            WAITING_POSTER: [MessageHandler(filters.ALL & ~filters.COMMAND, plink_receive_poster)],
            WAITING_PLINK_FILE: [MessageHandler(filters.ALL & ~filters.COMMAND, plink_receive_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    # ─── batch conversation ───────────────────────────
    batch_conv = ConversationHandler(
        entry_points=[CommandHandler("batch", batch_start)],
        states={
            BATCH_COLLECTING: [
                CommandHandler("batchdone", batch_done),
                MessageHandler(filters.ALL & ~filters.COMMAND, batch_receive_file),
            ]
        },
        fallbacks=[CommandHandler("cancel", batch_cancel)],
    )

    # ─── broadcast conversation ───────────────────────
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={WAITING_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)]},
        fallbacks=[CommandHandler("cancel", broadcast_cancel)],
    )

    # ─── shortener conversation ───────────────────────
    shortener_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(shortener_callback, pattern="^sh_add$")
        ],
        states={
            S_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, sh_receive_name)],
            S_API:  [MessageHandler(filters.TEXT & ~filters.COMMAND, sh_receive_api)],
            S_DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, sh_receive_domain)],
            S_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sh_receive_note)],
            S_DURATION: [CallbackQueryHandler(sh_receive_duration_callback, pattern="^shdur_")],
        },
        fallbacks=[CommandHandler("cancel", sh_cancel)],
    )

    # Register all handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("admin", add_admin_handler))
    app.add_handler(CommandHandler("deladmin", del_admin_handler))
    app.add_handler(CommandHandler("admins", list_admins_handler))
    app.add_handler(CommandHandler("ban", ban_handler))
    app.add_handler(CommandHandler("unban", unban_handler))
    app.add_handler(CommandHandler("banned", banned_list_handler))
    app.add_handler(CommandHandler("shortener", shortener_menu))

    app.add_handler(glink_conv)
    app.add_handler(plink_conv)
    app.add_handler(batch_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(shortener_conv)

    # Callback handlers
    app.add_handler(CallbackQueryHandler(batch_done_callback, pattern="^batch_done_"))
    app.add_handler(CallbackQueryHandler(shortener_callback, pattern="^sh_"))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("🤖 Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
