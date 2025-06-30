import os
import re
import logging
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("TELEG")
ALLOWED_USER_ID = 6264741586
sessions = {}

def is_authorized(user_id: int) -> bool:
    return user_id == ALLOWED_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied.")
        return
    await update.message.reply_text(
        "👋 Hey BRO! Send your messages.\n"
        "Use /calcy to start continuous adding of plain numbers."
    )

async def calcy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied.")
        return

    if user_id in sessions:
        await update.message.reply_text(
            "⚠️ Session active. Send 'stop', 'cancel', or a message with 'ZARxxx' to end it."
        )
    else:
        sessions[user_id] = 0.0
        await update.message.reply_text(
            "🔢 Calcy session started! Send numbers to add.\n"
            "Send 'stop' or 'cancel' to finish."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You're not authorized to use this bot.")
        return

    text = update.message.text.strip()

    if user_id in sessions:
        zar_amounts = [float(x) for x in re.findall(r'ZAR([\d.]+)', text)]
        if zar_amounts:
            total_zar = sum(zar_amounts)
            sessions[user_id] += total_zar
            total = sessions.pop(user_id)
            await update.message.reply_text(
                f"📩 SBI message detected! ✅ Total ZAR amount: {total_zar:.2f}"
            )
            return

        text_lower = text.lower()
        if text_lower in ('stop', 'cancel', 'end'):
            total = sessions.pop(user_id)
            await update.message.reply_text(f"✅ Session ended. Total amount: {total:.2f}")
            return

        numbers = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
        if numbers:
            sessions[user_id] += sum(numbers)
            await update.message.reply_text(
                f"➕ Added {sum(numbers):.2f}. Current total: {sessions[user_id]:.2f}✅"
            )
        else:
            await update.message.reply_text("❌ No numbers found. Send something like '100' or '45.50'.")
        return

    amounts = [float(x) for x in re.findall(r'ZAR([\d.]+)', text)]
    if amounts:
        total = sum(amounts)
        await update.message.reply_text(f"✅ Total ZAR amount: {total:.2f}")
    else:
        await update.message.reply_text("❌ No ZAR amounts found.")

async def handle_healthcheck(request):
    return web.Response(text="I'm alive!")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle_healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Webserver running on port {port}")

def main():
    # Start aiohttp webserver in background (in a new asyncio task)
    loop = asyncio.get_event_loop()
    loop.create_task(start_webserver())

    # Create Telegram bot application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calcy", calcy))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 Telegram bot started and polling...")
    application.run_polling()  # This internally runs the event loop

if __name__ == '__main__':
    main()
