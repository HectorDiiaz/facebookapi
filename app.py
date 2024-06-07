import os
import logging
from flask import Flask, request, jsonify
import requests
from asgiref.wsgi import WsgiToAsgi


app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Leer variables de entorno
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

# Verificar si las variables de entorno se están leyendo correctamente
if not VERIFY_TOKEN or not ACCESS_TOKEN:
    logging.error("Las variables de entorno VERIFY_TOKEN o ACCESS_TOKEN no están configuradas correctamente.")
else:
    logging.info("Las variables de entorno se han leído correctamente.")

@app.route('/')
def home():
    logging.info("Home endpoint accessed")
    return "Hello, World!"

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    logging.info(f"Echo endpoint accessed with data: {data}")
    return jsonify(data)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        logging.info(f"Webhook verification request received with token: {verify_token} and challenge: {challenge}")

        if verify_token == VERIFY_TOKEN:
            return str(challenge)
        logging.warning("Invalid verification token")
        return 'Token de verificación inválido', 403

    elif request.method == 'POST':
        data = request.get_json()
        logging.info(f"Webhook POST request received with data: {data}")

        # Procesa el mensaje recibido
        if data['object'] == 'whatsapp_business_account':
            for entry in data['entry']:
                for change in entry['changes']:
                    if change['field'] == 'messages':
                        message_event = change['value']
                        for message in message_event['messages']:
                            if message['type'] == 'text':
                                text = message['text']['body']
                                from_number = message['from']
                                logging.info(f"Received message from {from_number}: {text}")
                                # Envía una respuesta automática
                                send_whatsapp_message(from_number, f"Recibido: {text}")

        return 'EVENTO RECIBIDO', 200

@app.route('/validate_token', methods=['GET'])
def validate_token():
    url = 'https://graph.facebook.com/debug_token'
    params = {
        'input_token': ACCESS_TOKEN,
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    data = response.json()
    logging.info(f"Token validation response: {data}")
    return jsonify(data)

def send_whatsapp_message(phone_number_id, to_number, message_text):
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
            "preview_url": False,
            "body": message_text
        }
    }

    logging.info(f"Sending message to {to_number} using phone_number_id {phone_number_id}: {message_text}")
    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"Response from WhatsApp API: {response.json()}")
    return response.json()

# Convertir la aplicación Flask a ASGI usando WsgiToAsgi
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
