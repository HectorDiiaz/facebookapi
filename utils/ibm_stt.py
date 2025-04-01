import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(file_path):
    api_key = os.getenv("IBM_API_KEY")
    url = os.getenv("IBM_STT_URL")

    authenticator = IAMAuthenticator(api_key)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)

    with open(file_path, 'rb') as audio_file:
        result = stt.recognize(
            audio=audio_file,
            content_type='audio/ogg;codecs=opus',  # WhatsApp usa este formato
            model='es-ES_BroadbandModel'  # Puedes cambiar el idioma aquí
        ).get_result()

    try:
        return result['results'][0]['alternatives'][0]['transcript']
    except (IndexError, KeyError):
        return "No se pudo transcribir el audio."
