import pandas as pd
import logging
import os
from utils import normalize_name

def combine_names(df):
    """
    Combina columnas de nombres y apellidos en 'Nombre_Completo'.
    Si ya existe 'Nombre_Completo', no se realiza ningún cambio.
    """
    if 'Apellidos' in df.columns and 'Nombres' in df.columns:
        df['Nombre_Completo'] = df['Apellidos'] + ' ' + df['Nombres']
        logging.info("✅ [Nombres] Se combinó 'Apellidos' y 'Nombres' en 'Nombre_Completo'")
    else:
        if 'Nombre_Completo' not in df.columns:
            df['Nombre_Completo'] = df.index.astype(str)
            logging.info("⚠️ [Nombres] 'Nombre_Completo' no se encontró; se asignaron índices como nombres")
        else:
            logging.info("ℹ️ [Nombres] 'Nombre_Completo' ya existe, sin cambios")
    return df

def compare_with_local_database(df_form, local_db_path):
    """
    Compara el DataFrame del formulario con la base local y genera la columna 'Coincide'.
    """
    if not os.path.exists(local_db_path):
        error_msg = f"No se encontró la base local en: {local_db_path}"
        logging.error(f"❌ [Comparación] {error_msg}")
        raise FileNotFoundError(error_msg)

    # Leer la base local (columna 'NOMBRE')
    try:
        local_data = pd.read_excel(local_db_path, usecols=['NOMBRE'])
        logging.info("✅ [Comparación] Base local leída correctamente")
    except Exception as e:
        logging.error(f"❌ [Comparación] Error al leer la base local: {str(e)}", exc_info=True)
        raise e

    # Normalización de datos
    df_form['Nombre_Completo'] = df_form['Nombre_Completo'].apply(normalize_name)
    local_data['NOMBRE'] = local_data['NOMBRE'].apply(normalize_name)
    logging.info("ℹ️ [Comparación] Datos normalizados para la comparación")

    # Verificar coincidencias
    df_form['Coincide'] = df_form['Nombre_Completo'].isin(local_data['NOMBRE'])
    logging.info("✅ [Comparación] Columna 'Coincide' generada en el DataFrame")
    return df_form

def validate_data(form_data_path: str, local_db_path: str) -> pd.DataFrame:
    """
    Lee dos archivos Excel: uno del formulario y otro de la base local,
    combina nombres y genera la columna 'Coincide'.
    Retorna el DataFrame validado.
    """
    logging.info("ℹ️ [Validación] Iniciando la validación de datos")

    if not form_data_path:
        logging.warning("⚠️ [Validación] No se proporcionó el archivo de 'form data'")
        return pd.DataFrame()

    if not os.path.isfile(form_data_path):
        error_msg = f"No se encontró el archivo de form data: {form_data_path}"
        logging.error(f"❌ [Validación] {error_msg}")
        raise FileNotFoundError(error_msg)

    try:
        # LEER CON FORMATOS ESPECÍFICOS
        df_forms = pd.read_excel(
            form_data_path,
            dtype={
                'Número de cuenta bancaria': str,
                'Número de cuenta Interbancaria': str,
                'Nro. de Documento': str,
                'RUC': str,
                'Fecha de Emisión': str,
                'Número de cuenta bancaria (tercero)': str,
                'Número de cuenta Interbancaria (tercero)': str
            }
        )
        logging.info("✅ [Validación] Archivo de form data leído correctamente")
    except Exception as e:
        logging.error(f"❌ [Validación] Error al leer el archivo de form data: {str(e)}", exc_info=True)
        raise e

    if df_forms.empty:
        logging.warning("⚠️ [Validación] El archivo de form data está vacío")
        return pd.DataFrame()

    # Combinar nombres si es necesario
    df_forms = combine_names(df_forms)

    # Comparar con la base local
    logging.info(f"ℹ️ [Validación] Comparando con la base local: {local_db_path}")
    df_result = compare_with_local_database(df_forms, local_db_path)

    logging.info("✅ [Validación] Validación completada. DataFrame listo para usarse")
    return df_result

if __name__ == "__main__":
    # Configuración básica de logging para ejecución directa
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Solicitar rutas al usuario en consola
    form_data_path = input("Ruta de Excel de form data: ").strip()
    local_db_path  = input("Ruta de Excel de Base local: ").strip()

    try:
        df_val = validate_data(form_data_path, local_db_path)
        print("\nDataFrame validado (primeras filas):")
        print(df_val.head())
    except Exception as e:
        print(f"Error en la validación: {e}")
