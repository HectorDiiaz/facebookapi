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

# Función para enviar un mensaje de WhatsApp
def send_whatsapp_message(phone_number_id, to_number, message_payload):
    url = f'https://graph.facebook.com/v19.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=message_payload)
    logging.info(f"Response from WhatsApp API: {response.json()}")
    return response.json()

# Función para enviar el menú interactivo
def send_menu(phone_number_id, to_number):
    menu_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Selecciona una opción"
            },
            "body": {
                "text": "Por favor, elige una de las siguientes opciones:"
            },
            "footer": {
                "text": "Gracias por usar nuestro servicio"
            },
            "action": {
                "button": "Ver Opciones",
                "sections": [
                    {
                        "title": "Menú Principal",
                        "rows": [
                            {
                                "id": "option_1",
                                "title": "Enviar una imagen",
                                "description": "Recibe una imagen de nuestro catálogo"
                            },
                            {
                                "id": "option_2",
                                "title": "Enviar un audio",
                                "description": "Escucha un audio informativo"
                            },
                            {
                                "id": "option_3",
                                "title": "Enviar una ubicación",
                                "description": "Obtén nuestra ubicación"
                            },
                            {
                                "id": "option_4",
                                "title": "Enviar un documento",
                                "description": "Descarga un documento"
                            },
                            {
                                "id": "option_5",
                                "title": "Enviar un video",
                                "description": "Mira un video explicativo"
                            },
                            {
                                "id": "option_6",
                                "title": "Salir",
                                "description": "Finaliza la conversación"
                            }
                        ]
                    }
                ]
            }
        }
    }
    send_whatsapp_message(phone_number_id, to_number, menu_payload)

# Función para manejar las selecciones del menú
def handle_menu_selection(phone_number_id, to_number, selected_option):
    if selected_option == "option_1":
        # Enviar una imagen
        image_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "image",
            "image": {
                "link": "https://example.com/path/to/your/image.jpg",  # URL de la imagen
                "caption": "Aquí tienes la imagen solicitada."
            }
        }
        send_whatsapp_message(phone_number_id, to_number, image_payload)

    elif selected_option == "option_2":
        # Enviar un audio
        audio_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "audio",
            "audio": {
                "link": "https://example.com/path/to/your/audio.mp3"  # URL del audio
            }
        }
        send_whatsapp_message(phone_number_id, to_number, audio_payload)

    elif selected_option == "option_3":
        # Enviar una ubicación
        location_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "location",
            "location": {
                "latitude": -34.6037,
                "longitude": -58.3816,
                "name": "Nuestra Ubicación",
                "address": "Buenos Aires, Argentina"
            }
        }
        send_whatsapp_message(phone_number_id, to_number, location_payload)

    elif selected_option == "option_4":
        # Enviar un documento
        document_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "document",
            "document": {
                "link": "https://example.com/path/to/your/document.pdf",  # URL del documento
                "filename": "documento.pdf"
            }
        }
        send_whatsapp_message(phone_number_id, to_number, document_payload)

    elif selected_option == "option_5":
        # Enviar un video
        video_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "video",
            "video": {
                "link": "https://example.com/path/to/your/video.mp4",  # URL del video
                "caption": "Aquí tienes el video solicitado."
            }
        }
        send_whatsapp_message(phone_number_id, to_number, video_payload)

    elif selected_option == "option_6":
        # Salir
        exit_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias por usar nuestro servicio. ¡Adiós!"
            }
        }
        send_whatsapp_message(phone_number_id, to_number, exit_payload)

    else:
        # Opción no reconocida, enviar el menú nuevamente
        send_menu(phone_number_id, to_number)

# Ruta y lógica del webhook
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
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        message_event = change.get('value', {})
                        phone_number_id = message_event.get('metadata', {}).get('phone_number_id')
                        for message in message_event.get('messages', []):
                            if message.get('type') == 'text':
                                text = message['text']['body']
                                from_number = message['from']
                                logging.info(f"Received message from {from_number}: {text}")

                                # Verificar si el mensaje es una selección del menú
                                if message.get('interactive', {}).get('type') == 'list_response':
                                    selected_option = message['interactive']['list_response']['id']
                                    handle_menu_selection(phone_number_id, from_number, selected_option)
                                else:
                                    # Enviar el menú si el mensaje no es una selección
                                    send_menu(phone_number_id, from_number)

        return 'EVENTO RECIBIDO', 200

# Convertir la aplicación Flask a ASGI usando WsgiToAsgi
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
