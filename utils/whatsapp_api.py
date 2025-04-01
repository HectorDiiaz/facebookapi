import os
import requests

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID")

def download_audio(media_id):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Paso 1: Obtener la URL del archivo
    url_response = requests.get(
        f"https://graph.facebook.com/v19.0/{media_id}",
        headers=headers
    )

    try:
        audio_url = url_response.json()["url"]
    except KeyError:
        print("Error al obtener URL del audio. Respuesta:")
        print(url_response.json())
        raise Exception("No se pudo obtener la URL del audio.")

    # Paso 2: Descargar el archivo
    response = requests.get(audio_url, headers=headers)

    content_type = response.headers.get("Content-Type", "")
    print(f"Content-Type del audio: {content_type}")

    if "audio/ogg" not in content_type:
        print("Advertencia: El archivo no parece ser un .ogg válido.")

    file_path = "input.ogg"
    with open(file_path, "wb") as f:
        f.write(response.content)

    # Paso 3: Validar archivo descargado
    if not os.path.exists(file_path):
        raise FileNotFoundError("El archivo de audio no se guardó correctamente.")

    file_size = os.path.getsize(file_path)
    print(f"Archivo descargado: {file_path} ({file_size} bytes)")

    if file_size < 1000:
        print("Advertencia: El archivo descargado es muy pequeño, puede estar corrupto.")

    return file_path