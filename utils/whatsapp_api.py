import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID")

def download_audio(media_id):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    url_response = requests.get(
        f"https://graph.facebook.com/v19.0/{media_id}",
        headers=headers
    )
    audio_url = url_response.json()["url"]

    audio_data = requests.get(audio_url, headers=headers).content
    file_path = "input.ogg"
    with open(file_path, "wb") as f:
        f.write(audio_data)

    return file_path

def send_text_response(to_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
