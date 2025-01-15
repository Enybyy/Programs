import os
import unicodedata
import yaml
import json
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def get_drive_service(service_account_file, scopes):
    """
    Crea el servicio de Google Drive utilizando credenciales de la variable
    de entorno GOOGLE_APPLICATION_CREDENTIALS o un archivo local.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", service_account_file)

    if not credentials_path:
        raise ValueError("Las credenciales no están configuradas. "
                         "Asegúrate de que 'GOOGLE_APPLICATION_CREDENTIALS' o el parámetro 'service_account_file' esté disponible.")

    try:
        # Verificar si las credenciales están codificadas en Base64
        credentials_bytes = base64.b64decode(credentials_path)
        credentials_dict = json.loads(credentials_bytes.decode("utf-8"))
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    except (base64.binascii.Error, json.JSONDecodeError):
        # Si no es Base64 ni JSON, asumir que es una ruta de archivo
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)

    return build('drive', 'v3', credentials=credentials)

def load_config(config_file):
    """
    Carga configuraciones desde un archivo YAML.
    """
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error al cargar el archivo de configuración: {e}")
        return {}

def normalize_name(name):
    """
    Elimina espacios múltiples, tildes y pasa a MAYÚSCULAS.
    """
    name = " ".join(name.split())  # Eliminar espacios múltiples
    return ''.join(
        (c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    ).upper()
