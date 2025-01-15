import unicodedata
import yaml

# Para conectarnos a Google Drive
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def get_drive_service(service_account_file, scopes):
    """
    Crea el servicio de Google Drive utilizando service_account_file y scopes.
    """
    credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
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
    import unicodedata
    return ''.join(
        (c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    ).upper()
