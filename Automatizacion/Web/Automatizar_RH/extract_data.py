import os
import logging
import tempfile
import pandas as pd
import pdfplumber

# Importar la función para descargar desde Drive
from googleapiclient.http import MediaIoBaseDownload
from utils import get_drive_service

def download_pdf_from_drive(drive_service, file_id, output_path):
    """
    Descarga un archivo de Google Drive usando su ID y lo guarda en output_path.
    """
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
        logging.error(f"Error al descargar el archivo con ID {file_id}: {e}")
        return False

def extract_text_from_pdf(pdf_path, output_folder):
    """
    Extrae el texto de un PDF ya descargado y lo guarda en output_folder con extensión .txt.
    """
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_txt = os.path.join(output_folder, f"{base_name}.txt")

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

def extract_data_from_validated(service_account_file, df_validated):
    """
    Para cada fila con Coincide=True y 'Cargar Documento RH (PDF)',
    se asume que la URL es algo como 'https://drive.google.com/open?id=...'.
    Se extrae el fileId, se descarga el PDF a una carpeta temporal y se extrae su texto.
    Retorna la ruta base del directorio temporal creado.
    """
    logging.info("== Iniciando descarga de PDFs desde Google Drive y extracción de texto ==")

    # Crear el servicio
    drive_service = get_drive_service(service_account_file, ["https://www.googleapis.com/auth/drive"])

    # Crear la carpeta temporal
    tempdir = tempfile.mkdtemp(prefix="pdf_extract_")
    pdf_folder = os.path.join(tempdir, "pdfs")
    text_folder = os.path.join(tempdir, "extracted_text")
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)

    # Filtrar las filas
    df_ok = df_validated[df_validated['Coincide'] == True].copy()
    if 'Cargar Documento RH (PDF)' not in df_ok.columns:
        logging.warning("No existe la columna 'Cargar Documento RH (PDF)' en df_validated.")
        return tempdir

    for _, row in df_ok.iterrows():
        pdf_url = str(row["Cargar Documento RH (PDF)"]).strip()
        if not pdf_url:
            continue

        # Extraer el ID del URL (por ej. https://drive.google.com/open?id=1RNu8332u3z-xxx)
        if "id=" not in pdf_url:
            logging.warning(f"La URL {pdf_url} no contiene 'id=' => No se puede extraer fileId.")
            continue

        file_id = pdf_url.split("id=")[-1]
        nombre = row.get("Nombre_Completo", f"user_{_}")

        # Ruta local donde guardaremos el PDF
        local_pdf_path = os.path.join(pdf_folder, f"{nombre}.pdf")

        if download_pdf_from_drive(drive_service, file_id, local_pdf_path):
            extract_text_from_pdf(local_pdf_path, text_folder)
        else:
            logging.warning(f"No se pudo descargar o procesar el PDF para: {pdf_url}")

    logging.info(f"== PDFs y texto generados en carpeta temporal: {tempdir} ==")
    return tempdir

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Pequeña prueba
    import pandas as pd

    excel_path = input("Ruta de Excel validado: ").strip()
    service_account_file = input("Ruta de credenciales JSON: ").strip()
    df_val = pd.read_excel(excel_path)

    # Descarga PDFs y extrae textos
    tempdir = extract_data_from_validated(service_account_file, df_val)
    print(f"Carpeta temporal: {tempdir}")
