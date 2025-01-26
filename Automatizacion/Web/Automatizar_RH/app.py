from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import io
import zipfile
import tempfile
import logging
import pandas as pd
import shutil
from utils import load_config
from validate_data import validate_data
from extract_data import extract_data_from_validated
from fill_data import process_and_fill_data
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'clave-segura-desarrollo')
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    logging.info("== Iniciando start_process ==")

    # Resetear sesión previa
    session.clear()

    # Manejo de credenciales
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not encoded_credentials:
        logging.error("Credenciales de Google no configuradas")
        return "Error: Configuración de Google incompleta", 500

    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_file:
            temp_file.write(decoded_credentials)
            service_account_file = temp_file.name
    except Exception as e:
        logging.error(f"Error decodificando credenciales: {e}")
        return "Error procesando credenciales", 500

    # Validar credenciales
    try:
        load_config(service_account_file)
    except DefaultCredentialsError as e:
        logging.error(f"Credenciales inválidas: {e}")
        return "Credenciales de Google inválidas", 500

    # Procesar archivos subidos
    form_file = request.files.get("form_data_file")
    local_file = request.files.get("local_db_file")
    
    try:
        # Guardar archivos temporalmente
        temp_files = []
        form_data_path = local_db_path = ""
        
        if form_file and form_file.filename:
            temp_form = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            form_file.save(temp_form.name)
            form_data_path = temp_form.name
            temp_files.append(temp_form.name)
            logging.info(f"Form data guardado en: {temp_form.name}")

        if local_file and local_file.filename:
            temp_local = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            local_file.save(temp_local.name)
            local_db_path = temp_local.name
            temp_files.append(temp_local.name)
            logging.info(f"Base local guardada en: {temp_local.name}")

        # Proceso principal
        df_val = validate_data(form_data_path, local_db_path)
        tempdir = extract_data_from_validated(service_account_file, df_val)
        text_folder = os.path.join(tempdir, "extracted_text")
        df_final = process_and_fill_data(df_val, text_folder, local_db_path)

        # Almacenar en sesión
        session['validated_df'] = df_val.to_json()
        session['final_df'] = df_final.to_json()
        session['temp_dir'] = tempdir
        session['service_account_file'] = service_account_file

    except HttpError as e:
        logging.error(f"Error Google Drive: {e}")
        return f"Error en Google Drive: {e}", 500
    except Exception as e:
        logging.error(f"Error general: {e}", exc_info=True)
        return f"Error inesperado: {e}", 500
    finally:
        # Limpiar archivos temporales
        for f in temp_files:
            if os.path.exists(f):
                os.unlink(f)
        if 'service_account_file' in locals():
            os.unlink(service_account_file)

    return redirect(url_for("results"))

@app.route("/results")
def results():
    if 'validated_df' not in session:
        return redirect(url_for("index"))
    return render_template("results.html")

# Funciones de descarga mejoradas
def generate_download(df_key, filename):
    if df_key not in session:
        return "Datos no disponibles", 400
    
    try:
        df = pd.read_json(session[df_key])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"Error generando {filename}: {e}")
        return "Error generando archivo", 500

@app.route("/download-validated")
def download_validated():
    return generate_download('validated_df', "DatosValidados.xlsx")

@app.route("/download-final")
def download_final():
    return generate_download('final_df', "ResultadoFinal.xlsx")

@app.route("/download-pdfs")
def download_pdfs():
    if 'temp_dir' not in session or not os.path.exists(session['temp_dir']):
        return "No hay PDFs disponibles", 400

    pdf_folder = os.path.join(session['temp_dir'], "pdfs")
    if not os.path.exists(pdf_folder):
        return "Carpeta de PDFs no encontrada", 400

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    if os.path.getsize(pdf_path) > 0:
                        zf.write(pdf_path, arcname=filename)
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="PDFsDescargados.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        logging.error(f"Error generando ZIP: {e}")
        return "Error comprimiendo archivos", 500
    
@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    if 'final_df' not in session or 'temp_dir' not in session:
        return "No hay datos disponibles", 400

    # Convertir DataFrame a Excel en memoria
    df_final = pd.read_json(session['final_df'])
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False)
    excel_buffer.seek(0)

    # Crear ZIP con Excel y PDFs
    pdf_folder = os.path.join(session['temp_dir'], "pdfs")
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Agregar Excel
        zf.writestr("ResultadoFinal.xlsx", excel_buffer.read())
        
        # Agregar PDFs
        if os.path.exists(pdf_folder):
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    if os.path.getsize(pdf_path) > 0:
                        zf.write(pdf_path, f"pdfs/{filename}")

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="ResultadoFinal_y_PDFs.zip",
        mimetype="application/zip"
    )

@app.route("/cleanup", methods=['POST'])
def cleanup():
    try:
        if 'temp_dir' in session and os.path.exists(session['temp_dir']):
            shutil.rmtree(session['temp_dir'])
        session.clear()
        return "Limpieza exitosa", 200
    except Exception as e:
        logging.error(f"Error en limpieza: {e}")
        return "Error en limpieza", 500

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5000)