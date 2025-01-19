from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import io
import zipfile
import tempfile
import logging
import pandas as pd

from utils import load_config
from validate_data import validate_data
from extract_data import extract_data_from_validated
from fill_data import process_and_fill_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-segura'

# Variables globales para DEMO
CURRENT_VALIDATED_DF = None
CURRENT_FINAL_DF = None
CURRENT_TEMP_DIR = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    global CURRENT_VALIDATED_DF, CURRENT_FINAL_DF, CURRENT_TEMP_DIR

    logging.info("== Iniciando start_process ==")

    # Obtener las credenciales desde la variable de entorno
    service_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account_file:
        logging.error("La variable de entorno 'GOOGLE_APPLICATION_CREDENTIALS' no está configurada.")
        return "Error: Credenciales no configuradas.", 500

    # Recibir archivos
    form_file = request.files.get("form_data_file")
    local_file = request.files.get("local_db_file")

    form_data_path = ""
    local_db_path = ""

    try:
        if form_file and form_file.filename:
            temp_form = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            form_file.save(temp_form.name)
            form_data_path = temp_form.name
            logging.info(f"Form data subido a: {temp_form.name}")

        if local_file and local_file.filename:
            temp_local = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            local_file.save(temp_local.name)
            local_db_path = temp_local.name
            logging.info(f"Base local subida a: {temp_local.name}")

        # 1) Validar
        logging.info("== Iniciando validación de datos ==")
        df_val = validate_data(form_data_path, local_db_path)
        if df_val is None or df_val.empty:
            logging.error("La validación de datos no produjo resultados.")
            return "Error: No se generaron datos validados.", 500

        CURRENT_VALIDATED_DF = df_val
        logging.info(f"Datos validados: {len(df_val)} filas.")

        # 2) Descargar PDFs de Drive y extraer texto
        logging.info("== Extrayendo datos de PDFs ==")
        tempdir = extract_data_from_validated(service_account_file, df_val)
        if not tempdir or not os.path.exists(tempdir):
            logging.error("Error al extraer datos de PDFs.")
            return "Error: No se pudo extraer datos de los PDFs.", 500

        CURRENT_TEMP_DIR = tempdir
        logging.info(f"Datos extraídos en: {tempdir}")

        # 3) Llenar datos
        logging.info("== Procesando y llenando datos ==")
        text_folder = os.path.join(tempdir, "extracted_text")
        df_final = process_and_fill_data(df_val, text_folder, local_db_path)
        if df_final is None or df_final.empty:
            logging.error("El procesamiento de datos no produjo resultados finales.")
            return "Error: No se generaron datos finales.", 500

        CURRENT_FINAL_DF = df_final
        logging.info(f"Datos finales procesados: {len(df_final)} filas.")

        return redirect(url_for("results"))

    except Exception as e:
        logging.exception("Error en el flujo de procesamiento de datos.")
        return f"Error interno del servidor: {str(e)}", 500

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/download-validated")
def download_validated():
    global CURRENT_VALIDATED_DF
    if CURRENT_VALIDATED_DF is None or CURRENT_VALIDATED_DF.empty:
        logging.warning("Intento de descarga sin datos validados en memoria.")
        return "No hay datos validados en memoria.", 400

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        CURRENT_VALIDATED_DF.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="DatosValidados.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download-final")
def download_final():
    global CURRENT_FINAL_DF
    if CURRENT_FINAL_DF is None or CURRENT_FINAL_DF.empty:
        logging.warning("Intento de descarga sin datos finales en memoria.")
        return "No hay datos finales en memoria.", 400

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        CURRENT_FINAL_DF.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="ResultadoFinal.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download-pdfs")
def download_pdfs():
    global CURRENT_TEMP_DIR
    if not CURRENT_TEMP_DIR or not os.path.exists(CURRENT_TEMP_DIR):
        logging.warning("Intento de descarga sin PDFs disponibles.")
        return "No hay PDFs", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")
    if not os.path.exists(pdf_folder):
        logging.warning("El directorio de PDFs no existe.")
        return "No se encontraron PDFs.", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, filename)
                with open(pdf_path, "rb") as f:
                    zf.writestr(filename, f.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="PDFsDescargados.zip",
        mimetype="application/zip"
    )

@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    """
    Crea un ZIP que contiene el Excel final y los PDFs descargados.
    """
    global CURRENT_FINAL_DF, CURRENT_TEMP_DIR
    if CURRENT_FINAL_DF is None or CURRENT_FINAL_DF.empty:
        logging.warning("Intento de descarga combinada sin datos finales en memoria.")
        return "No hay datos finales en memoria.", 400
    if not CURRENT_TEMP_DIR or not os.path.exists(CURRENT_TEMP_DIR):
        logging.warning("Intento de descarga combinada sin PDFs disponibles.")
        return "No hay PDFs descargados.", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")

    # 1) Convertir el DataFrame final a un archivo Excel en memoria
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        CURRENT_FINAL_DF.to_excel(writer, index=False)
    excel_buffer.seek(0)

    # 2) Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Agregar el Excel al ZIP
        zf.writestr("ResultadoFinal.xlsx", excel_buffer.read())

        # Agregar los PDFs al ZIP
        if os.path.exists(pdf_folder):
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    with open(pdf_path, "rb") as f:
                        zf.writestr(f"pdfs/{filename}", f.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="ResultadoFinal_y_PDFs.zip",
        mimetype="application/zip"
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app.run(debug=True, port=5000)
