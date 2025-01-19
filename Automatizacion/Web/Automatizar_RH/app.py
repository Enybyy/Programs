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
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

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
        return "Error: las credenciales de Google no están configuradas.", 500

    # Validar si las credenciales son válidas
    try:
        load_config(service_account_file)  # Asegúrate de que este método valida las credenciales
    except DefaultCredentialsError as e:
        logging.error(f"Error al cargar las credenciales de Google: {e}")
        return "Error al cargar las credenciales de Google. Verifique su configuración.", 500

    # Recibir archivos
    form_file = request.files.get("form_data_file")
    local_file = request.files.get("local_db_file")

    form_data_path = ""
    local_db_path = ""

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

    try:
        # 1) Validar
        df_val = validate_data(form_data_path, local_db_path)
        CURRENT_VALIDATED_DF = df_val

        # 2) Descargar PDFs de Drive y extraer texto
        tempdir = extract_data_from_validated(service_account_file, df_val)
        CURRENT_TEMP_DIR = tempdir

        # 3) Llenar datos
        text_folder = os.path.join(tempdir, "extracted_text")
        df_final = process_and_fill_data(df_val, text_folder, local_db_path)
        CURRENT_FINAL_DF = df_final

    except HttpError as e:
        logging.error(f"Error al interactuar con la API de Google Drive: {e}")
        return f"Error al descargar o procesar archivos de Google Drive: {e}", 500
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return f"Ocurrió un error inesperado: {e}", 500

    return redirect(url_for("results"))

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/download-validated")
def download_validated():
    global CURRENT_VALIDATED_DF
    if CURRENT_VALIDATED_DF is None or CURRENT_VALIDATED_DF.empty:
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
        return "No hay PDFs", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")
    if not os.path.exists(pdf_folder):
        return "No se encontraron PDFs.", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, filename)
                # Validar que el archivo no esté vacío
                if os.path.getsize(pdf_path) > 0:
                    try:
                        with open(pdf_path, "rb") as f:
                            zf.writestr(filename, f.read())
                    except Exception as e:
                        logging.warning(f"Error al procesar el archivo {filename}: {e}")
                else:
                    logging.warning(f"Archivo {filename} está vacío y será omitido.")

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="PDFsDescargados.zip",
        mimetype="application/zip"
    )

@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    global CURRENT_FINAL_DF, CURRENT_TEMP_DIR
    if CURRENT_FINAL_DF is None or CURRENT_FINAL_DF.empty:
        return "No hay datos finales en memoria.", 400
    if not CURRENT_TEMP_DIR or not os.path.exists(CURRENT_TEMP_DIR):
        return "No hay PDFs descargados.", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")

    # Convertir el DataFrame final a un archivo Excel en memoria
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        CURRENT_FINAL_DF.to_excel(writer, index=False)
    excel_buffer.seek(0)

    # Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Agregar el Excel al ZIP
        zf.writestr("ResultadoFinal.xlsx", excel_buffer.read())

        # Agregar los PDFs al ZIP
        if os.path.exists(pdf_folder):
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    if os.path.getsize(pdf_path) > 0:
                        try:
                            with open(pdf_path, "rb") as f:
                                zf.writestr(f"pdfs/{filename}", f.read())
                        except Exception as e:
                            logging.warning(f"Error al procesar el archivo {filename}: {e}")
                    else:
                        logging.warning(f"Archivo {filename} está vacío y será omitido.")

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="ResultadoFinal_y_PDFs.zip",
        mimetype="application/zip"
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5000)
