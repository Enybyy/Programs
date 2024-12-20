import pandas as pd
from utils import normalize_name
import os
import logging
import yaml

# Leer configuraciones desde config.yaml
def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error al cargar el archivo de configuración: {e}")
        raise e

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Verificar dependencias necesarias
def check_dependencies():
    try:
        import googleapiclient.discovery
        from google.oauth2.service_account import Credentials
        logging.info("Dependencias verificadas correctamente.")
    except ImportError as e:
        logging.error("Faltan dependencias necesarias. Ejecuta: pip install google-api-python-client google-auth")
        raise e

# Leer datos de Google Sheets
def read_google_sheet(service_account_file, spreadsheet_id, sheet_name):
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials

    credentials = Credentials.from_service_account_file(
        service_account_file, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
        values = result.get('values', [])
        if not values:
            logging.warning("No se encontraron datos en la hoja de cálculo.")
            return pd.DataFrame()

        headers = values[0]
        data = values[1:]
        return pd.DataFrame(data, columns=headers)
    except Exception as e:
        logging.error(f"Error al leer Google Sheets: {e}")
        raise e

# Combinar nombres y apellidos
def combine_names(dataframe):
    try:
        dataframe['Nombre-Completo'] = dataframe['Apellidos'].str.strip() + ' ' + dataframe['Nombres'].str.strip()
        dataframe['Nombre-Completo'] = dataframe['Nombre-Completo'].apply(normalize_name)
        return dataframe
    except KeyError as e:
        logging.error(f"Columnas faltantes para combinar nombres: {e}")
        raise e

# Comparar con la base local
def compare_with_local_database(form_data, local_database_path):
    if not os.path.exists(local_database_path):
        logging.error(f"La base de datos local no se encuentra en: {local_database_path}")
        raise FileNotFoundError("Base de datos local no encontrada.")

    try:
        local_data = pd.read_excel(local_database_path)
        form_data['Nombre Normalizado'] = form_data['Nombre-Completo'].str.strip().str.lower()
        local_data['Nombre Normalizado'] = local_data['NOMBRE'].str.strip().str.lower()
        form_data['Coincide'] = form_data['Nombre Normalizado'].isin(local_data['Nombre Normalizado'])
        form_data.drop(columns=['Nombre Normalizado'], inplace=True)
        return form_data
    except KeyError as e:
        logging.error(f"Error en las columnas de la base local: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error al comparar con la base local: {e}")
        raise e

# Guardar resultados en un archivo
def save_results(dataframe, output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dataframe.to_excel(output_path, index=False)
        logging.info(f"Resultados guardados en: {output_path}")
    except Exception as e:
        logging.error(f"Error al guardar los resultados: {e}")
        raise e

# Función principal
def main(config):
    try:
        check_dependencies()

        logging.info("Leyendo datos de Google Sheets...")
        form_data = read_google_sheet(
            config['service_account_file'],
            config['spreadsheet_id'],
            config['sheet_name']
        )

        if form_data.empty:
            logging.warning("No se pudo leer la hoja de cálculo o está vacía.")
            return

        logging.info("Combinando columnas de nombres y apellidos...")
        form_data = combine_names(form_data)

        logging.info("Comparando con la base de datos local...")
        result_data = compare_with_local_database(form_data, config['local_database_path'])

        logging.info("Guardando resultados...")
        save_results(result_data, config['output_path'])

    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    CONFIG_FILE = 'config.yaml'
    config = load_config(CONFIG_FILE)
    main(config)
