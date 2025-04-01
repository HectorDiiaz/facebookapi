import os
import logging
from flask import Flask, request
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv

from utils.ibm_stt import transcribe_audio
from utils.whatsapp_api import download_audio, send_text_response

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        return str(challenge) if token == VERIFY_TOKEN else 'Invalid token', 403

    elif request.method == 'POST':
        data = request.get_json()
        logging.info(f"Data recibida: {data}")

        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                messages = change.get('value', {}).get('messages', [])
                for message in messages:
                    if message.get('type') == 'audio':
                        from_number = message['from']
                        media_id = message['audio']['id']

                        audio_path = download_audio(media_id)
                        transcript = transcribe_audio(audio_path)

                        send_text_response(from_number, transcript)

        return 'OK', 200

asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=8000)
