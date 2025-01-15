import os
import re
import logging
import dateparser
import pandas as pd
import tempfile

from utils import normalize_name, load_config
from validate_data import validate_data
from extract_data import extract_data_from_validated

def extract_data_from_text(text: str) -> dict:
    extracted = {
        'Total': None,
        'Fecha': None,
        'Serie': None,
        'Recibo': None
    }
    match_total = re.search(r'(?:Total Neto Recibido\s*S/|Total Neto Recibido:\s*)([\d.,]+)', text, re.IGNORECASE)
    if match_total:
        val_str = match_total.group(1).replace(',', '')
        try:
            extracted['Total'] = float(val_str)
        except:
            pass

    match_fecha_a = re.search(r'Fecha de Emisión\s*Tipo de Moneda\s*([\d]{2}/[\d]{2}/[\d]{4})', text, re.IGNORECASE)
    match_fecha_b = re.search(r'Fecha de emisión\s*(\d{1,2}\s+de\s+\w+\s+del\s+\d{4})', text, re.IGNORECASE)
    if match_fecha_a:
        extracted['Fecha'] = match_fecha_a.group(1)
    elif match_fecha_b:
        fecha_text = match_fecha_b.group(1)
        parsed = dateparser.parse(fecha_text, languages=['es'])
        if parsed:
            extracted['Fecha'] = parsed.strftime('%d/%m/%Y')

    match_num_a = re.search(r'N°\s*(E\d+)-(\d+)', text)
    match_num_b = re.search(r'Nro:\s*(E\d+)\s*-\s*(\d+)', text)
    if match_num_a:
        extracted['Serie'] = match_num_a.group(1)
        extracted['Recibo'] = match_num_a.group(2)
    elif match_num_b:
        extracted['Serie'] = match_num_b.group(1)
        extracted['Recibo'] = match_num_b.group(2)

    return extracted

def remove_suffix_dotzero(value):
    if isinstance(value, str) and value.endswith('.0'):
        return value[:-2]
    return value

def process_and_fill_data(
    df_validated: pd.DataFrame,
    text_folder: str,
    local_db_path: str
) -> pd.DataFrame:
    """
    1) Lee la base local de 'local_db_path'.
    2) Usa df_validated, busca Coincide=True.
    3) Extrae datos de .txt (en text_folder) para cada persona.
    4) Rellena la base local y retorna un DataFrame final (SIN escribir a disco).
    """
    logging.info("== Iniciando llenado de datos finales en memoria ==")
    
    dtype_for_base_local = {
        "BANCO": str, "NRO DE RUC": str, "NRO DE DOCUMENTO": str,
        "NRO DOC TERCERO": str, "NRO DE CUENTA": str, "CCI": str
    }
    base_local = pd.read_excel(local_db_path, dtype=dtype_for_base_local)

    # Normalizar
    base_local['NOMBRE'] = base_local['NOMBRE'].apply(normalize_name)
    df_validated['Nombre_Completo'] = df_validated['Nombre_Completo'].apply(normalize_name)

    # Convertir ciertas columnas a str
    fields_to_cast = [
        "FECHA DE EMISION", "NRO SERIE", "NRO RECIBO",
        "NOMBRE DEL TERCERO", "TIPO DOC TERCERO",
        "TIPO DE DOCUMENTO", "COMENTARIOS RRHH"
    ]
    for field in fields_to_cast:
        if field in base_local.columns:
            base_local[field] = base_local[field].astype(str)

    for idx, row in base_local.iterrows():
        nombre = row['NOMBRE']
        matched = df_validated[(df_validated['Nombre_Completo']==nombre) & (df_validated['Coincide']==True)]
        if matched.empty:
            continue

        mr = matched.iloc[0]

        # Leer texto .txt si existe
        txt_path = os.path.join(text_folder, f"{nombre}.txt")
        extracted_data = {}
        if os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    pdf_text = f.read()
                extracted_data = extract_data_from_text(pdf_text)
            except Exception as e:
                logging.error(f"Error al leer {txt_path}: {e}")

        # Rellenar
        if 'FECHA DE EMISION' in base_local.columns:
            base_local.at[idx, 'FECHA DE EMISION'] = extracted_data.get('Fecha', '')
        if 'NRO SERIE' in base_local.columns:
            base_local.at[idx, 'NRO SERIE'] = extracted_data.get('Serie', '')
        if 'NRO RECIBO' in base_local.columns:
            base_local.at[idx, 'NRO RECIBO'] = extracted_data.get('Recibo', '')

        # RUC
        if 'RUC' in mr and 'NRO DE RUC' in base_local.columns:
            base_local.at[idx, 'NRO DE RUC'] = mr['RUC']

        # Verificar tercero
        emitir_tercero = str(mr.get('Emitir Recibo por Honorarios a un tercero.', '')).lower().strip()
        tipo_doc_persona = mr.get('Tipo de Documento', '')
        nro_doc_persona = mr.get('Nro. de Documento', '')

        # Tercero
        ap_ter = mr.get('Apellidos (tercero)', '')
        nom_ter = mr.get('Nombres (tercero)', '')
        tipo_doc_ter = mr.get('Tipo de Documento (tercero)', '')
        nro_doc_ter = mr.get('Nro. de Documento (tercero)', '')

        if emitir_tercero in ["si", "sí"]:
            # Persona
            if 'TIPO DE DOCUMENTO' in base_local.columns:
                base_local.at[idx, 'TIPO DE DOCUMENTO'] = tipo_doc_persona
            if 'NRO DE DOCUMENTO' in base_local.columns:
                base_local.at[idx, 'NRO DE DOCUMENTO'] = nro_doc_persona

            # Tercero
            nombre_completo_tercero = (ap_ter + ' ' + nom_ter).strip()
            if 'NOMBRE DEL TERCERO' in base_local.columns:
                base_local.at[idx, 'NOMBRE DEL TERCERO'] = nombre_completo_tercero.upper()
            if 'TIPO DOC TERCERO' in base_local.columns:
                base_local.at[idx, 'TIPO DOC TERCERO'] = tipo_doc_ter
            if 'NRO DOC TERCERO' in base_local.columns:
                base_local.at[idx, 'NRO DOC TERCERO'] = nro_doc_ter

            # Banco del tercero
            ent_banc_3 = mr.get('Entidad Bancaria (tercero)', '')
            nom_banc_3 = mr.get('Nombre de Entidad Bancaria (tercero)', '')
            if ent_banc_3.lower() == 'otro banco':
                bank_str = nom_banc_3
            else:
                bank_str = ent_banc_3
            bank_str = normalize_name(bank_str)
            if 'BANCO' in base_local.columns:
                base_local.at[idx, 'BANCO'] = bank_str

            if 'NRO DE CUENTA' in base_local.columns:
                base_local.at[idx, 'NRO DE CUENTA'] = mr.get('Número de cuenta bancaria (tercero)', '')
            if 'CCI' in base_local.columns:
                base_local.at[idx, 'CCI'] = mr.get('Número de cuenta Interbancaria (tercero)', '')
        else:
            # NO a tercero
            if 'TIPO DE DOCUMENTO' in base_local.columns:
                base_local.at[idx, 'TIPO DE DOCUMENTO'] = tipo_doc_persona
            if 'NRO DE DOCUMENTO' in base_local.columns:
                base_local.at[idx, 'NRO DE DOCUMENTO'] = nro_doc_persona

            # Vaciar datos tercero
            if 'NOMBRE DEL TERCERO' in base_local.columns:
                base_local.at[idx, 'NOMBRE DEL TERCERO'] = ''
            if 'TIPO DOC TERCERO' in base_local.columns:
                base_local.at[idx, 'TIPO DOC TERCERO'] = ''
            if 'NRO DOC TERCERO' in base_local.columns:
                base_local.at[idx, 'NRO DOC TERCERO'] = ''

            ent_banc = mr.get('Entidad Bancaria', '')
            nom_banc = mr.get('Nombre de Entidad Bancaria', '')
            if ent_banc.lower() == 'otro banco':
                bank_str = nom_banc
            else:
                bank_str = ent_banc
            bank_str = normalize_name(bank_str)
            if 'BANCO' in base_local.columns:
                base_local.at[idx, 'BANCO'] = bank_str

            if 'NRO DE CUENTA' in base_local.columns:
                base_local.at[idx, 'NRO DE CUENTA'] = mr.get('Número de cuenta bancaria', '')
            if 'CCI' in base_local.columns:
                base_local.at[idx, 'CCI'] = mr.get('Número de cuenta Interbancaria', '')

    # Convertir a str y limpiar 'nan'
    base_local = base_local.astype(str)
    base_local = base_local.replace([r'^\s*nan\s*$', r'^nan$', r'^None$', r'^NaN$'], '', regex=True)
    for col in base_local.columns:
        base_local[col] = base_local[col].apply(remove_suffix_dotzero)

    logging.info("== Llenado completado en memoria. Retornando DataFrame final. ==")
    return base_local

def run_all_in_memory():
    """
    Demostración en consola:
    1) Pide ruta de form data y base local.
    2) Valida => df_validated
    3) Descarga PDFs con extract_data_from_validated => extrae texto
    4) Llena datos => df_final
    5) Guarda en un NamedTemporaryFile
    """
    import logging
    logging.basicConfig(level=logging.INFO)

    # Cargar configuraciones
    config = load_config("config.yaml")
    form_data_path = input("Ruta de Excel FORM data: ").strip()
    local_db_path = input("Ruta de Excel local (base local): ").strip()

    # 1) Validación
    df_val = validate_data(form_data_path, local_db_path)

    # 2) Descarga PDFs y extrae textos
    tempdir = extract_data_from_validated(config['service_account_file'], df_val)
    text_folder = os.path.join(tempdir, "extracted_text")

    # 3) Llenado final
    df_final = process_and_fill_data(df_val, text_folder, local_db_path)

    # 4) Guardar excel final
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df_final.to_excel(tmp.name, index=False)
        logging.info(f"Archivo final guardado en: {tmp.name}")

if __name__ == "__main__":
    run_all_in_memory()

# C:\Users\nav\Downloads\ABBY\Eliud\Proyectos\RH\Excel\JORNADA NOV.xlsx
# C:\Users\nav\Downloads\ELIUD\Descargas express\PAGO DE RH - FORMULARIO (Respuestas).xlsx