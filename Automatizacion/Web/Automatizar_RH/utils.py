import unicodedata

# ----------------------- CONFIGURACIÓN ------------------------- #

def load_config(config_file):
    """
    Carga configuraciones desde un archivo YAML.

    Parámetros:
        config_file (str): Ruta del archivo YAML de configuración.

    Retorna:
        dict: Diccionario con las configuraciones cargadas.
    """
    import yaml
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error al cargar el archivo de configuración: {e}")
        return {}

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
    
