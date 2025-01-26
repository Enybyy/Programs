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


"""

    ew0KICAidHlwZSI6ICJzZXJ2aWNlX2FjY291bnQiLA0KICAicHJvamVjdF9pZCI6ICJwcnVlYmFyaC00NDI0MTIiLA0KICAicHJpdmF0ZV9rZXlfaWQiOiAiMTJlMWU1ZTkwZWU5ZDU4ZGIxODk2MTYzMDZlYjNlMzQ4NmI1YjY4NiIsDQogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRRGFoS3B5YWNHK0F6UWJcbmNIWEZSZ2I4STVwWU1qQ0wrWTRIcjRaKzNKQUVVbUU2ejZUVEdZNG9kOW1ic3owdDk3S0p1WGl0VDRtb0ZweTBcbktvMFVFZThvOHhEZkQyMithVkhhYjMwblBtZDRIRGR2Qmw3L2tHbjdtYkFwT3hiQkx3YXBvbEx6OUs4L2xHZFdcbmNnZGJpVjZlUWtzR25RVWJmWDZwL1RMS3p4ZHhWN3U3a1pkdVgrTmZkbzgxVWZNMk9nUEJZY25zUDQvM2RIOUlcbldreFMvMUNWNk1IQURSdmd0cmlPV2JUYjg0MGo1cUN0SlJ0ZlJ6b2orazJmSDNjdURmQVdXQysyMGliRzRXTmxcbkVzc1lpQlJpMW5mK0g3N0ZYbmdBU0NFN0NlQzBMVEJ2TWxZOXhTU1BxSXh3UUVIcVY4eUJoS1Y1L0QvSWlKZEhcbmViTTNZUTNOQWdNQkFBRUNnZ0VBRnhLN0RLbXVFMm96TGxLSm5QTHYrZCtvaEhlSU9MOTVCOGE0NU54Vk9KK2Fcbk5LT0lPK0lPNktiL0N6bTUxQWk3aVY5VUpyaW5TR0JhMjR0Q3FrUGFoUEJsYjZncFpsbW9rdkFDdndvUDB0Ym5cbjQ0bEFycXVKQlZBTkVjMXpjYUtOaVl2aVJuQW5zUWJ5Z21ZMzhLcG9tejFVdnJZRnZBbGNQb2JGdmpSdnZUL2NcblY2MUJ0NlpiN003dFE1TjRlK1l6V293dlJwbVVBaFE0blVQQlJPTmtEbWdIRWlNWWhIN0hZSUNsOWh4d3FhOURcbkp5UWtla043RXcwNFRuVVkzcTlXMGhHZUJzSzVBeXk0MDNBYnh2YzBwOS9BYnpRM0w2RVNHSU5UTDZJNFJucHFcbmZGTlFQTHBKTHNiQ29RSzZBRzNuRWsyOWN6OTkxQVZqT3JEQ2RkSjVBUUtCZ1FEdVVoZlZWeDEvdUJtU05MYTFcbnpBTmVFL3lqaUlQTUtqbnROejJsWFJ6RmZwRkVRZlFEcis1SFgxdWsvaTRTc21kOXhFZ1BnR3hHOG95K3N0SHVcbjZLVCsvU2VKS1p4bnhrUFhpVzhPaEFqeVBuWDNEK2l6cGl0ZkFPMUNpVnNsZ0hGa2xjM0Y4OWkzMjBRcUk5azFcbmVGTVdOY2dLQkhRcEZSdzQySFRCSXltZ2lRS0JnUURxdW9IK1NLNUh0NGtDUEtob1dmd1RjdEEzdjNLUldxK3Jcbkt2NkU1dW8wQTZoaEFEek9nMkZPbFdRNURMMDhxSXY2dUE2aCttRnBWVG83NjRMVU1QczhOL1A1L3gvYW1waGRcbitxNGZ3a0pVTVR4aXlDa3hkQ0Q3REMwbit5elBtTm1tNXNyTGVsM2FLeEphVVBDT1FKa0EzbG9RVXdTbE9IdkpcblJTUnNFSHVLSlFLQmdRRFY4d2NJZEx1NzFEZklwT0ErVnhmUzFwaWc2MForL0kyaVkweEpiMDBNRS9NdjF4SE1cbldaM05uMUx6eldqcFNoWlV0dWlHV2lGYWxCYzhmK2F0MTFlQXZ4NUdLZ0FLdmRoYjREcStTbFNKdlA5RVBKa0lcbjVxM2JEVWJ5eThMeTZOdGpsSVQyS0ZLdncvM3U0dDMxL2I2Qm11aXA3Wk9tNmhlN0JML1VQOC80R1FLQmdRQ1hcbktuSFpMemw5MmtjVDk3aUZLNTVaY0JHRU5YazAvdkF2RGN0SUQrWTRoVHFFN2NBN1J3VDl0TndNbVpXdFlPWjFcbkd0L2hsUHZ5OS80KzVKY216RHlnTlhDY1NaOWNDeitoRm5YWTRpUVJVSHdSS2RMTmxIcEE4MENKaFFzQXp2RXNcbnVXbFV6WU52bzFsNGJMUGZDTjhBWGpJbVhUQ2FydHVaYlR2ZGxHZmJPUUtCZ0NReFBReVBOWlRtZ1JDTk5qUUNcbnBIYWIrUG5ETjVJbFFOT2dzZTIyN0trZ25JZ0xRL2FnY1QyMHNESEpzSFFOVHVGVXVvWmw4MURJOWtTTGlGOWZcbnAxK3dJTWNvU2JCcnlka0tYSllTRU5ySWt4cWhPMDhuOU91YS8rN2VGbXJNd1dsczVhdWJ5eXgxdk4xaXJjMkxcbkNCQnlPU1IvTURnbCtQMEo0Wlp0U0xNQVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwNCiAgImNsaWVudF9lbWFpbCI6ICJwcnVlYmEtcmhAcHJ1ZWJhcmgtNDQyNDEyLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwNCiAgImNsaWVudF9pZCI6ICIxMDkxOTAwMjE0MzU0MzM4ODUzMzIiLA0KICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLA0KICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwNCiAgImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2VydHMiLA0KICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9wcnVlYmEtcmglNDBwcnVlYmFyaC00NDI0MTIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLA0KICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIg0KfQ==

"""