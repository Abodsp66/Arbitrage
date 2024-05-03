import requests
from flask import Flask, request

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = "7077125494:AAEfbQ6xjGvyz44aAy2fPVAS_yQFGgmwS44"

# Replace 'YOUR_WEBHOOK_URL' with your webhook URL provided by Telegram or your hosting provider
WEBHOOK_URL = "https://arbitrage-2smi.onrender.com"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    return response.json()

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    params = {"url": WEBHOOK_URL}
    response = requests.get(url, params=params)
    return response.json()

@app.route('/', methods=['POST'])
def handle_message():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data.get("message", {}).get("text", "")

    if "/start" in text:
        send_message(chat_id, "Hello!")

    return {"status": "OK"}

if __name__ == "__main__":
    # Set the webhook URL
    set_webhook()

    # Run the Flask app
    app.run(debug=True)
