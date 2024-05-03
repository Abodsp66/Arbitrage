import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = "YOUR_BOT_TOKEN"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    return response.json()

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if "/start" in text:
        send_message(chat_id, "Hello!")

def main():
    update_id = None
    while True:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        if update_id:
            url += f"?offset={update_id + 1}"
        response = requests.get(url)
        messages = response.json().get("result", [])

        for message in messages:
            if "message" in message:
                handle_message(message["message"])
                update_id = message["update_id"]

if __name__ == "__main__":
    main()
