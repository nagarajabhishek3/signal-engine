import requests

BOT_TOKEN = "8611656592:AAH1i1uQYCsYuioAeABBfAjN_3qmm7gIQII"
CHAT_ID = "403996503"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        return response.json()
    except Exception as e:
        print("Telegram Error:", e)
