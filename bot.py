import os
import re
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token from Render environment variable
BOT_TOKEN = os.environ.get("TELEG")

# Allowed user (BRO)
ALLOWED_USER_ID = 6264741586

# Sessions: user_id -> total_amount
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

    # No active session
    amounts = [float(x) for x in re.findall(r'ZAR([\d.]+)', text)]
    if amounts:
        total = sum(amounts)
        await update.message.reply_text(f"✅ Total ZAR amount: {total:.2f}")
    else:
        await update.message.reply_text("❌ No ZAR amounts found.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calcy", calcy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("🤖 Bot is running on Render for BRO only...")
    app.run_polling()

if __name__ == '__main__':
    main()
