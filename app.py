from flask import Flask, request, jsonify
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)

VERIFY_TOKEN = 'asdasdasdasdsa_token_123ñld_verify_token'
ACCESS_TOKEN = 'TU_TOKEN_DE_ACCESO'

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify(data)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if verify_token == VERIFY_TOKEN:
            return str(challenge)
        return 'Token de verificación inválido', 403

    elif request.method == 'POST':
        data = request.get_json()

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

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Convertir la aplicación Flask a ASGI usando WsgiToAsgi
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
