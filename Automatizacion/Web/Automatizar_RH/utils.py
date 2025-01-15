import os
import unicodedata
import yaml
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def get_drive_service(scopes):
    """
    Crea el servicio de Google Drive utilizando credenciales de la variable
    de entorno GOOGLE_APPLICATION_CREDENTIALS.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_path:
        raise ValueError("La variable de entorno 'GOOGLE_APPLICATION_CREDENTIALS' no está configurada.")

    # Si las credenciales están en formato Base64
    if credentials_path.startswith("{") or credentials_path.startswith("\"{"):
        import json
        credentials_dict = json.loads(credentials_path)
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    else:
        # Si las credenciales están en un archivo local
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
