import os
import unicodedata
import yaml
import json
import base64
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def get_drive_service(service_account_file, scopes):
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", service_account_file)
    
    if not credentials_path:
        raise ValueError("Credenciales no configuradas")

    try:
        # Intentar decodificar como Base64
        try:
            credentials_bytes = base64.b64decode(credentials_path)
            credentials_dict = json.loads(credentials_bytes.decode("utf-8"))
        except (base64.binascii.Error, json.JSONDecodeError):
            # Si falla, cargar desde archivo
            with open(credentials_path, 'r') as f:
                credentials_dict = json.load(f)
        
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        return build('drive', 'v3', credentials=credentials)
    
    except Exception as e:
        logging.error(f"Error crítico con credenciales: {str(e)}")
        raise

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
