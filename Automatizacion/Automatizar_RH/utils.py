from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import unicodedata

# ----------------------- CONEXIÓN ------------------------- #

def get_drive_service(service_account_file, scopes):
    credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    return build('drive', 'v3', credentials=credentials)

def get_gspread_client(service_account_file, scopes):
    credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    return build('sheets', 'v4', credentials=credentials)

# ----------------------- LISTAR ------------------------- #

def listar_archivos_drive(drive_service, cantidad=10):
    try:
        results = drive_service.files().list(
            pageSize=cantidad,
            fields="files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])
        if not files:
            print('No se encontraron archivos en tu Google Drive.')
        else:
            print('Archivos encontrados:')
            for file in files:
                print(f"Nombre: {file['name']}, ID: {file['id']}, Tipo: {file['mimeType']}")
        return files
    except Exception as e:
        print(f"Error al listar archivos: {e}")
        
# ----------------------- LIMPIAR ------------------------- #

# Función para eliminar tildes y espacios extra
def normalize_name(name):
    name = " ".join(name.split())  # Eliminar espacios múltiples
    return ''.join(
        (c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    ).upper()
    
