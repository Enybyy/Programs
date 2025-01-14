import pandas as pd
import logging
import os
from utils import normalize_name

def combine_names(df):
    """
    Combina columnas de nombres y apellidos en 'Nombre_Completo'.
    Ajusta según tu caso real. 
    Si ya tienes 'Nombre_Completo', no hagas nada.
    """
    if 'Apellidos' in df.columns and 'Nombres' in df.columns:
        df['Nombre_Completo'] = df['Apellidos'] + ' ' + df['Nombres']
    else:
        # Si no existen esas columnas y tampoco está 'Nombre_Completo'
        if 'Nombre_Completo' not in df.columns:
            df['Nombre_Completo'] = df.index.astype(str)
    return df

def compare_with_local_database(df_form, local_db_path):
    """
    Compara df_form con la base local (otro Excel), creando la columna 'Coincide'.
    """
    if not os.path.exists(local_db_path):
        raise FileNotFoundError(f"No se encontró la base local en: {local_db_path}")

    # Leer la base local (columna 'NOMBRE')
    local_data = pd.read_excel(local_db_path, usecols=['NOMBRE'])

    # Normalizar
    df_form['Nombre_Completo'] = df_form['Nombre_Completo'].apply(normalize_name)
    local_data['NOMBRE']       = local_data['NOMBRE'].apply(normalize_name)

    # Coincidencia
    df_form['Coincide'] = df_form['Nombre_Completo'].isin(local_data['NOMBRE'])
    return df_form

def validate_data(
    form_data_path: str,
    local_db_path: str
) -> pd.DataFrame:
    """
    Lee dos Excels: uno de 'form data' y otro 'base local', 
    combina nombres y genera la columna 'Coincide'.
    Retorna un DataFrame con toda la info.
    """
    logging.info("== Iniciando validación de datos sin Google ==")

    if not form_data_path:
        logging.warning("No se proporcionó un Excel de 'form data'.")
        return pd.DataFrame()

    if not os.path.isfile(form_data_path):
        raise FileNotFoundError(f"No se encontró el archivo de form data: {form_data_path}")

    # Leer el Excel de form data
    df_forms = pd.read_excel(form_data_path)
    if df_forms.empty:
        logging.warning("El form data está vacío.")
        return pd.DataFrame()

    # Combinar nombres, si aplica
    df_forms = combine_names(df_forms)

    # Comparar con la base local
    logging.info(f"Comparando con la base local: {local_db_path}")
    df_result = compare_with_local_database(df_forms, local_db_path)

    logging.info("== Validación completada. Retornando DataFrame en memoria ==")
    return df_result

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    # Pedir rutas al usuario en consola
    form_data_path = input("Ruta de Excel de form data: ").strip()
    local_db_path  = input("Ruta de Excel de Base local: ").strip()

    df_val = validate_data(form_data_path, local_db_path)
    print("\nDataFrame validado (primeras filas):")
    print(df_val.head())
