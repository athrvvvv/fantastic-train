# main.py
import threading
from flask import Flask
from telegram_bot import main as start_bot  # move your bot code to telegram_bot.py

app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram bot is running."

def run_bot():
    start_bot()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=8000)
