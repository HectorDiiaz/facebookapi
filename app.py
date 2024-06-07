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

def send_whatsapp_message(to_number, message_text):
    url = f'https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'text': {'body': message_text}
    }

    logging.info(f"Sending message to {to_number}: {message_text}")
    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"Response from WhatsApp API: {response.json()}")
    return response.json()

# Convertir la aplicación Flask a ASGI usando WsgiToAsgi
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
