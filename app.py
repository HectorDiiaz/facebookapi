import os
import logging
from flask import Flask, request
import requests
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv

from utils.ibm_stt import transcribe_audio

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Leer variables de entorno
load_dotenv()
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

# Función para enviar un mensaje de texto por WhatsApp
def send_text_message(phone_number_id, to_number, message):
    url = f'https://graph.facebook.com/v19.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"Respuesta WhatsApp: {response.json()}")
    return response.json()

# Función para descargar el audio usando media_id
def download_audio(media_id):
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    # Paso 1: obtener la URL
    url_response = requests.get(
        f'https://graph.facebook.com/v19.0/{media_id}',
        headers=headers
    )
    try:
        audio_url = url_response.json()["url"]
    except KeyError:
        logging.error("Respuesta al obtener media URL:", url_response.json())
        raise Exception("No se pudo obtener la URL del audio.")

    # Paso 2: descargar el archivo
    audio_data = requests.get(audio_url, headers=headers).content
    file_path = "input.ogg"
    with open(file_path, "wb") as f:
        f.write(audio_data)

    return file_path

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return str(challenge)
        return 'Token inválido', 403

    elif request.method == 'POST':
        data = request.get_json()
        logging.info(f"Data recibida: {data}")

        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    phone_number_id = value.get('metadata', {}).get('phone_number_id')
                    messages = value.get('messages', [])

                    for message in messages:
                        from_number = message['from']

                        if message.get('type') == 'audio':
                            media_id = message['audio']['id']

                            try:
                                audio_path = download_audio(media_id)
                                transcript = transcribe_audio(audio_path)
                                logging.info(f"Transcripción: {transcript}")
                                send_text_message(phone_number_id, from_number, transcript)
                            except Exception as e:
                                logging.error(f"Error procesando audio: {str(e)}")
                                send_text_message(phone_number_id, from_number, "Ocurrió un error al procesar tu mensaje de voz.")

                        else:
                            # Si no es audio, responder con un mensaje predeterminado
                            send_text_message(phone_number_id, from_number, "Envíame un mensaje de voz y te lo transcribo.")

        return 'EVENTO RECIBIDO', 200

# Adaptar a ASGI para Render
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
