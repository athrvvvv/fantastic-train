from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re,os

# Replace this with your actual bot token from BotFather
tele_token = os.environ.get("TELEG")
BOT_TOKEN = str(tele_token)

# Allowed user (BRO)
ALLOWED_USER_ID = 6264741586

# Store sessions: user_id -> total_amount
sessions = {}

# Function to check access
def is_authorized(user_id):
    return user_id == ALLOWED_USER_ID

# /start command
def start(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        update.message.reply_text("❌ Access Denied.")
        return
    update.message.reply_text(
        "👋 Hey BRO! Send your messages.\n"
        "Use /calcy to start continuous adding of plain numbers.\n"
        # "In /calcy mode, send plain numbers to add or send a full SBI message containing 'ZARxxx' to automatically add and end session.\n"
        # "You can also send 'stop' or 'cancel' to end the session manually."
    )

# /calcy command: start session for user
def calcy(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        update.message.reply_text("❌ Access Denied.")
        return
    
    if user_id in sessions:
        update.message.reply_text("⚠️ You already have an active session. Send 'stop', 'cancel', or a SBI message containing 'ZARxxx' to end it.")
    else:
        sessions[user_id] = 0.0
        update.message.reply_text(
            "🔢 Calcy session started! Send plain numbers to add.\n"
            "Send 'stop' or 'cancel' to finish and get the total.\n"
            # "Or send your SBI message containing 'ZARxxx' to add and auto-end."
        )

# Message handler (handles both normal and session messages)
def handle_message(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        update.message.reply_text("❌ You're not authorized to use this bot.")
        return

    text = update.message.text.strip()

    # Check if user is in a session
    if user_id in sessions:
        # Check if text contains ZAR amounts (full SBI message)
        zar_amounts = [float(x) for x in re.findall(r'ZAR([\d.]+)', text)]

        if zar_amounts:
            # Add all ZAR amounts found
            total_zar = sum(zar_amounts)
            sessions[user_id] += total_zar
            total = sessions.pop(user_id)  # End session automatically
            update.message.reply_text(
                f"📩 SBI message detected! ✅ Total ZAR amount: {total_zar:.2f} \n"
                # f"📩 SBI message detected. Added {total_zar:.2f} ZAR.\n"
                # f"✅ Session ended. Grand total: {total:.2f} ZAR."
            )
            return

        # If no ZAR amounts, check for stop words as before
        text_lower = text.lower()
        if text_lower in ('stop', 'cancel', 'end'):
            total = sessions.pop(user_id)
            update.message.reply_text(f"✅ Session ended. Total amount: {total:.2f}")
            return
        
        # Otherwise, treat as plain numbers to add
        numbers = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
        if numbers:
            sessions[user_id] += sum(numbers)
            update.message.reply_text(f"➕ Added {sum(numbers):.2f}. Current total: {sessions[user_id]:.2f}✅")
        else:
            update.message.reply_text("❌ No numbers found in your message. Send numbers like '100' or '45.50'.")
        return

    # Outside session: look for ZAR-prefixed amounts like before
    amounts = [float(x) for x in re.findall(r'ZAR([\d.]+)', text)]
    if amounts:
        total = sum(amounts)
        update.message.reply_text(f"✅ Total ZAR amount: {total:.2f}")
    else:
        update.message.reply_text("❌ No ZAR amounts found.")

# Main function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("calcy", calcy))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("🤖 Bot is running for BRO only...")
    updater.idle()

if __name__ == '__main__':
    main()
