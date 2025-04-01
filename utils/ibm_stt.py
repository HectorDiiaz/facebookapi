import os
from dotenv import load_dotenv
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import ffmpeg

load_dotenv()

def convert_to_flac(input_path, output_path="converted.flac"):
    try:
        ffmpeg.input(input_path).output(output_path, ac=1).run(quiet=True, overwrite_output=True)
        print(f"Archivo convertido a FLAC: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error convirtiendo a FLAC: {e}")
        raise

def transcribe_audio(file_path):
    api_key = os.getenv("IBM_API_KEY")
    url = os.getenv("IBM_URL")

    authenticator = IAMAuthenticator(api_key)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)

    # Convertir el archivo OGG a FLAC
    flac_path = convert_to_flac(file_path)

    try:
        with open(flac_path, 'rb') as audio_file:
            print(f"Enviando archivo {flac_path} a IBM STT...")
            result = stt.recognize(
                audio=audio_file,
                content_type='audio/flac',
                model='es-ES_BroadbandModel'
            ).get_result()
            return result['results'][0]['alternatives'][0]['transcript']
    except Exception as e:
        print(f"ERROR IBM STT: {e}")
        raise
