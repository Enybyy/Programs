from utils import get_drive_service
from googleapiclient.http import MediaIoBaseDownload
import os
import pandas as pd
import pdfplumber

def download_pdf_from_drive(drive_service, file_id, output_path):
    """
    Descarga un archivo de Google Drive utilizando su ID.

    Parámetros:
        drive_service: Servicio autenticado de Google Drive.
        file_id (str): ID del archivo en Google Drive.
        output_path (str): Ruta donde se guardará el archivo descargado.

    Retorna:
        bool: True si la descarga fue exitosa, False en caso contrario.
    """
    try:
        request = drive_service.files().get_media(fileId=file_id)
        with open(output_path, "wb") as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Descargando... {int(status.progress() * 100)}%")
        return True
    except Exception as e:
        print(f"Error al descargar el archivo con ID {file_id}: {e}")
        return False

def process_matching_rows_with_drive(excel_path, pdf_folder, service_account_file):
    """
    Procesa las filas coincidentes en el archivo Excel y extrae datos de los PDFs desde Google Drive.

    Parámetros:
        excel_path (str): Ruta del archivo Excel con filas coincidentes.
        pdf_folder (str): Carpeta donde se almacenarán los PDFs descargados.
        service_account_file (str): Archivo de credenciales para Google API.

    Retorna:
        DataFrame: Datos combinados del Excel y los PDFs.
    """
    # Crear la carpeta de salida si no existe
    os.makedirs(pdf_folder, exist_ok=True)

    # Leer el archivo Excel
    data = pd.read_excel(excel_path)

    # Autenticarse con Google Drive
    drive_service = get_drive_service(service_account_file, ["https://www.googleapis.com/auth/drive"])

    # Filtrar solo las filas donde la columna 'Coincide' sea True
    matching_rows = data[data['Coincide'] == True]

    # Crear lista para almacenar datos combinados
    combined_data = []

    for _, row in matching_rows.iterrows():
        pdf_url = row["Cargar Documento RH (PDF)"]
        file_id = pdf_url.split("id=")[-1]  # Extraer el ID del archivo de la URL
        local_pdf_path = os.path.join(pdf_folder, f"{file_id}.pdf")

        if download_pdf_from_drive(drive_service, file_id, local_pdf_path):
            # Extraer datos del PDF
            pdf_data = extract_pdf_data(local_pdf_path)
            # Combinar los datos del Excel con los extraídos del PDF
            combined_entry = {**row.to_dict(), **pdf_data}
            combined_data.append(combined_entry)
        else:
            print(f"No se pudo descargar o procesar el archivo PDF para: {pdf_url}")

    # Convertir los datos combinados a DataFrame
    combined_df = pd.DataFrame(combined_data)

    return combined_df

def extract_pdf_data(pdf_path):
    """
    Extrae datos clave de un archivo PDF específico.

    Parámetros:
        pdf_path (str): Ruta del archivo PDF.

    Retorna:
        dict: Diccionario con los datos extraídos.
    """
    extracted_data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if "Monto a pagar" in text:
                    extracted_data['Monto'] = text.split("Monto a pagar:")[1].split()[0]
                if "Fecha de emisión" in text:
                    extracted_data['Fecha'] = text.split("Fecha de emisión:")[1].split()[0]
    except Exception as e:
        print(f"Error al procesar el archivo PDF: {e}")

    return extracted_data

# Ejemplo de uso
if __name__ == "__main__":
    EXCEL_PATH = "data/generated_files/resultados_comparacion.xlsx"
    PDF_FOLDER = "data/generated_files/pdfs"
    SERVICE_ACCOUNT_FILE = "API/credentials.json"

    # Procesar las filas coincidentes y extraer datos de los PDFs desde Google Drive
    result = process_matching_rows_with_drive(EXCEL_PATH, PDF_FOLDER, SERVICE_ACCOUNT_FILE)

    # Guardar el resultado en un nuevo archivo Excel
    OUTPUT_PATH = "data/generated_files/datos_combinados.xlsx"
    result.to_excel(OUTPUT_PATH, index=False)
    print(f"Datos combinados guardados en: {OUTPUT_PATH}")
