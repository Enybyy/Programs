import pandas as pd
from utils import normalize_name

# Configuración de archivos
SERVICE_ACCOUNT_FILE = 'API/credentials.json'  # Ruta a las credenciales
SPREADSHEET_ID = '1B8T0_TcVck9FPkS_cHYNSK1emLhTzkj-4YTN2-gIs-k'  # ID de la hoja de Google
SHEET_NAME = 'Hoja1'  # Nombre de la hoja
LOCAL_DATABASE_PATH = 'data/JORNADA NOV.xlsx'  # Base de datos local

# Verificar dependencias necesarias
def check_dependencies():
    try:
        import googleapiclient.discovery
        from google.oauth2.service_account import Credentials
    except ImportError as e:
        print("Error: Falta instalar las dependencias necesarias. Ejecuta: pip install google-api-python-client google-auth")
        raise e

# Función para leer datos de Google Sheets
def read_google_sheet(service_account_file, spreadsheet_id, sheet_name):
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials

    credentials = Credentials.from_service_account_file(
        service_account_file, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    values = result.get('values', [])

    if not values:
        print("No se encontraron datos en la hoja de cálculo.")
        return pd.DataFrame()

    # Convertir a DataFrame
    headers = values[0]
    data = values[1:]
    return pd.DataFrame(data, columns=headers)

# Función para combinar nombres y apellidos
def combine_names(dataframe):
    # Combinar las columnas 'Apellidos' y 'Nombres' en una nueva columna 'Nombre-Completo'
    dataframe['Nombre-Completo'] = dataframe['Apellidos'].str.strip() + ' ' + dataframe['Nombres'].str.strip()
    dataframe['Nombre-Completo'] = dataframe['Nombre-Completo'].apply(normalize_name)
    return dataframe

# Función para comparar con la base local
def compare_with_local_database(form_data, local_database_path):
    # Leer la base local
    local_data = pd.read_excel(local_database_path)

    # Normalizar nombres para evitar errores por mayúsculas/minúsculas o espacios
    form_data['Nombre Normalizado'] = form_data['Nombre-Completo'].str.strip().str.lower()
    local_data['Nombre Normalizado'] = local_data['NOMBRE'].str.strip().str.lower()

    # Comparar nombres
    form_data['Coincide'] = form_data['Nombre Normalizado'].isin(local_data['Nombre Normalizado'])

    # Eliminar la columna auxiliar
    form_data.drop(columns=['Nombre Normalizado'], inplace=True)

    return form_data

# Función principal
def main():
    try:
        # Verificar dependencias
        check_dependencies()

        # Leer datos del formulario
        print("Leyendo datos de Google Sheets...")
        form_data = read_google_sheet(SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SHEET_NAME)

        if form_data.empty:
            print("No se pudo leer la hoja de cálculo.")
            return

        # Combinar nombres y apellidos
        print("Combinando columnas de nombres y apellidos...")
        form_data = combine_names(form_data)

        # Comparar con la base local
        print("Comparando con la base de datos local...")
        result_data = compare_with_local_database(form_data, LOCAL_DATABASE_PATH)

        # Guardar resultados en un archivo
        output_path = 'data/generated_files/resultados_comparacion.xlsx'
        result_data.to_excel(output_path, index=False)
        print(f"Resultados guardados en: {output_path}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
