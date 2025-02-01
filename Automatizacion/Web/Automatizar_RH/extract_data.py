import os
import logging
import tempfile
import pandas as pd
import pdfplumber
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
                    logging.info(f"📥 Progreso descarga: {int(status.progress() * 100)}%")
        return True
    except Exception as e:
        logging.error(f"❌ Error descargando PDF (ID: {file_id}): {str(e)}")
        return False

def extract_text_from_pdf(pdf_path, output_folder):
    """
    Extrae el texto de un PDF ya descargado y lo guarda en output_folder con extensión .txt.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_txt = os.path.join(output_folder, f"{base_name}.txt")

        with pdfplumber.open(pdf_path) as pdf:
            with open(output_txt, "w", encoding="utf-8") as f:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        f.write(text + "\n")
        logging.info(f"✅ Texto extraído: {os.path.basename(output_txt)} ({os.path.getsize(output_txt)} bytes)")
        return True
    except Exception as e:
        logging.error(f"❌ Error extrayendo texto de {pdf_path}: {str(e)}")
        return False

def extract_data_from_validated(service_account_file, df_validated):
    """
    Descarga PDFs desde Google Drive y extrae su texto.
    Retorna la ruta base del directorio temporal creado.
    """
    logging.info("\n== 📦 INICIO DE EXTRACCIÓN DE DATOS ==")
    
    try:
        drive_service = get_drive_service(service_account_file, ["https://www.googleapis.com/auth/drive"])
        logging.info("🔑 Servicio de Google Drive inicializado correctamente")

        # Crear estructura de carpetas
        tempdir = tempfile.mkdtemp(prefix="pdf_extract_")
        pdf_folder = os.path.join(tempdir, "pdfs")
        text_folder = os.path.join(tempdir, "extracted_text")
        os.makedirs(pdf_folder, exist_ok=True)
        os.makedirs(text_folder, exist_ok=True)
        logging.info(f"📂 Directorio temporal creado: {tempdir}")

        # Filtrar registros válidos
        if 'Cargar Documento RH (PDF)' not in df_validated.columns:
            logging.warning("⚠️ Columna 'Cargar Documento RH (PDF)' no encontrada en los datos")
            return tempdir

        df_ok = df_validated[df_validated['Coincide'] == True].copy()
        total_files = len(df_ok)
        logging.info(f"🔍 Iniciando procesamiento de {total_files} PDFs")

        success_count = 0
        for idx, row in df_ok.iterrows():
            pdf_url = str(row["Cargar Documento RH (PDF)"]).strip()
            if not pdf_url:
                continue

            # Extraer ID del PDF
            if "id=" not in pdf_url:
                logging.warning(f"⚠️ URL inválida: {pdf_url}")
                continue

            file_id = pdf_url.split("id=")[-1]
            nombre = row.get("Nombre_Completo", f"registro_{idx}")
            local_pdf_path = os.path.join(pdf_folder, f"{nombre}.pdf")

            # Descargar y procesar PDF
            if download_pdf_from_drive(drive_service, file_id, local_pdf_path):
                if extract_text_from_pdf(local_pdf_path, text_folder):
                    success_count += 1
                    logging.info(f"✔️ Procesado exitosamente: {nombre}")
                else:
                    logging.warning(f"⚠️ Falló extracción de texto: {nombre}")
            else:
                logging.warning(f"⚠️ Falló descarga de PDF: {nombre}")

        logging.info(f"📊 Resultados de extracción: {success_count}/{total_files} exitosos")
        logging.info(f"== 🏁 EXTRACCIÓN COMPLETADA EN {tempdir} ==")

    except Exception as e:
        logging.critical(f"❌ Error crítico en extracción de datos: {str(e)}")
        raise

    return tempdir

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    try:
        excel_path = input("Ruta de Excel validado: ").strip()
        service_account_file = input("Ruta de credenciales JSON: ").strip()
        df_val = pd.read_excel(excel_path)
        
        tempdir = extract_data_from_validated(service_account_file, df_val)
        logging.info(f"🔍 Carpeta temporal generada: {tempdir}")
    except Exception as e:
        logging.error(f"❌ Error en ejecución manual: {str(e)}")