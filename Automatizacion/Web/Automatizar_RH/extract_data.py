import os
import logging
import tempfile
import pandas as pd
import pdfplumber
from googleapiclient.http import MediaIoBaseDownload
from utils import get_drive_service

def download_pdf_from_drive(drive_service, file_id, output_path):
    try:
        request = drive_service.files().get_media(fileId=file_id)
        with open(output_path, "wb") as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Descargando... {int(status.progress() * 100)}%")
        return True
    except Exception as e:
        logging.error(f"Error al descargar archivo con ID {file_id}: {e}")
        return False

def extract_text_from_pdf(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    txt_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
    output_txt = os.path.join(output_folder, txt_name)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(output_txt, "w", encoding="utf-8") as f:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        f.write(text + "\n")
        print(f"Texto extraído guardado en: {output_txt}")
    except Exception as e:
        logging.error(f"Error al extraer texto de {pdf_path}: {e}")

def extract_data_from_validated(
    service_account_file: str,
    df_validated: pd.DataFrame
) -> str:
    """
    Recibe un DataFrame validado y descarga PDFs + extrae texto en una carpeta temporal.
    Retorna la ruta base de la carpeta temporal.
    """
    logging.info("== Iniciando descarga de PDFs y extracción de texto (temporal) ==")

    drive_service = get_drive_service(service_account_file, ["https://www.googleapis.com/auth/drive"])

    tempdir = tempfile.mkdtemp(prefix="pdf_extract_")
    pdf_folder = os.path.join(tempdir, "pdfs")
    text_folder = os.path.join(tempdir, "extracted_text")
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)

    # Filtramos solo las filas con Coincide == True y que tengan 'Cargar Documento RH (PDF)'
    df_ok = df_validated[df_validated['Coincide'] == True].copy()
    if 'Cargar Documento RH (PDF)' not in df_ok.columns:
        logging.warning("No existe columna 'Cargar Documento RH (PDF)' en df_validated.")
        return tempdir

    for _, row in df_ok.iterrows():
        pdf_url = row["Cargar Documento RH (PDF)"]
        if not isinstance(pdf_url, str):
            continue

        file_id = pdf_url.split("id=")[-1].strip()
        nombre = row.get("Nombre_Completo", f"user_{_}")

        pdf_path = os.path.join(pdf_folder, f"{nombre}.pdf")
        if download_pdf_from_drive(drive_service, file_id, pdf_path):
            extract_text_from_pdf(pdf_path, text_folder)

    logging.info(f"== PDFs y texto generados en carpeta temporal: {tempdir} ==")
    return tempdir

if __name__ == "__main__":
    import yaml
    from validate_data import validate_data

    logging.basicConfig(level=logging.INFO)

    # Leer config
    with open("config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Pedir rutas
    form_data_path = input("Ruta de Excel FORM data (ENTER => Google Sheets): ").strip()
    local_db_path = input("Ruta de Excel local (base local): ").strip()

    # Validar
    df_val = validate_data(
        service_account_file=config['service_account_file'],
        spreadsheet_id=config['spreadsheet_id'],
        sheet_name=config['sheet_name'],
        form_data_path=form_data_path,
        local_db_path=local_db_path
    )

    # Extraer
    tempdir = extract_data_from_validated(config['service_account_file'], df_val)
    print(f"Archivos temporales en: {tempdir}")
