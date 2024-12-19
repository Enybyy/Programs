import utils

# Usar la función desde utils
try:
    drive_service = utils.get_drive_service('API/credentials.json', ['https://www.googleapis.com/auth/drive'])
    archivos = utils.listar_archivos_drive(drive_service)
    
    # Verificar si se encontraron archivos
    if archivos:
        print("Archivos encontrados en Google Drive:")
        for archivo in archivos:
            print(f"Nombre: {archivo['name']}, ID: {archivo['id']}, Tipo: {archivo['mimeType']}")
    else:
        print("No se encontraron archivos en Google Drive.")
except Exception as e:
    print(f"Error al conectar o listar archivos de Google Drive: {e}")
