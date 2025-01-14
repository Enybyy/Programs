from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import io
import zipfile
import tempfile
import logging

import pandas as pd

# Importar tus funciones "en memoria"
from validate_data import validate_data
from extract_data import extract_data_from_validated
from fill_data import process_and_fill_data
from utils import load_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cualquier-texto-seguro'  # Requerido para sesiones si quisieras usarlas

# Variables globales para DEMO (un solo usuario)
# En producción / multi-usuario conviene usar session u otra persistencia
CURRENT_VALIDATED_DF = None
CURRENT_FINAL_DF = None
CURRENT_TEMP_DIR = None  # carpeta temporal donde están los PDFs

@app.route("/")
def index():
    """
    Página inicial con el formulario para subir:
      - Excel de FORM data
      - Excel de BASE local
    Y un botón "Iniciar Proceso".
    """
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    """
    1) Recibe los archivos subidos (form_data y base_local).
    2) Los guarda en archivos temporales.
    3) Ejecuta validate_data, extract_data, fill_data.
    4) Guarda resultados en variables globales.
    5) Redirige a /results.
    """
    global CURRENT_VALIDATED_DF, CURRENT_FINAL_DF, CURRENT_TEMP_DIR

    # 1. Cargar config
    config = load_config("config.yaml")

    # 2. Verificar archivos subidos
    form_file = request.files.get("form_data_file")     # <input name="form_data_file" />
    local_file = request.files.get("local_db_file")     # <input name="local_db_file" />

    # Rutas vacías si no sube nada (para "Google Sheets" en form data)
    form_data_path = ""
    local_db_path = ""

    # 3. Guardar archivo form_data en un NamedTemporaryFile si no está vacío
    if form_file and form_file.filename != "":
        temp_form = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        form_file.save(temp_form.name)
        form_data_path = temp_form.name
        logging.info(f"Form data subido a: {temp_form.name}")

    # 4. Guardar archivo base_local en un NamedTemporaryFile si no está vacío
    if local_file and local_file.filename != "":
        temp_local = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        local_file.save(temp_local.name)
        local_db_path = temp_local.name
        logging.info(f"Base local subida a: {temp_local.name}")

    # 5. VALIDATE DATA
    df_val = validate_data(
        service_account_file=config['service_account_file'],
        spreadsheet_id=config['spreadsheet_id'],
        sheet_name=config['sheet_name'],
        form_data_path=form_data_path,  # si está vacío => usa Google Sheets
        local_db_path=local_db_path     # si está vacío => fallará la comparación
    )

    CURRENT_VALIDATED_DF = df_val  # Guardar en global

    # 6. EXTRACT PDFs (carpeta temporal)
    tempdir = extract_data_from_validated(config['service_account_file'], df_val)
    CURRENT_TEMP_DIR = tempdir

    # 7. FILL DATA
    #    - requiere: df_val, la carpeta con .txt, y la base local
    #    - si local_db_path está vacío, fallará => asumes que era obligatorio
    text_folder = os.path.join(tempdir, "extracted_text")
    df_final = process_and_fill_data(df_val, text_folder, local_db_path)

    CURRENT_FINAL_DF = df_final  # Guardar en global

    return redirect(url_for("results"))

@app.route("/results")
def results():
    """
    Página con botones para descargar:
      - Excel validado
      - Excel final
      - PDFs en ZIP
      - (Opcional) un ZIP con final + PDFs
    """
    return render_template("results.html")

@app.route("/download-validated")
def download_validated():
    """
    Envía el DataFrame validado (CURRENT_VALIDATED_DF) como Excel en memoria
    """
    global CURRENT_VALIDATED_DF
    if CURRENT_VALIDATED_DF is None or CURRENT_VALIDATED_DF.empty:
        return "No hay datos validados en memoria.", 400

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        CURRENT_VALIDATED_DF.to_excel(writer, index=False, sheet_name="DatosValidados")
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="DatosValidados.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download-final")
def download_final():
    """
    Envía el DataFrame final (CURRENT_FINAL_DF) como Excel en memoria
    """
    global CURRENT_FINAL_DF
    if CURRENT_FINAL_DF is None or CURRENT_FINAL_DF.empty:
        return "No hay datos finales en memoria.", 400

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        CURRENT_FINAL_DF.to_excel(writer, index=False, sheet_name="ResultadoFinal")
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="ResultadoFinal.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download-pdfs")
def download_pdfs():
    """
    Empaqueta los PDFs descargados en un ZIP y los envía
    """
    global CURRENT_TEMP_DIR
    if not CURRENT_TEMP_DIR or not os.path.exists(CURRENT_TEMP_DIR):
        return "No hay PDFs en memoria o la carpeta temporal no existe.", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")
    if not os.path.exists(pdf_folder):
        return "No se encontraron PDFs descargados.", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, filename)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                zf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="PDFsDescargados.zip",
        mimetype="application/zip"
    )

# Opcional: un ZIP con el Excel Final + PDFs
@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    """
    Crea un ZIP que contiene 'ResultadoFinal.xlsx' + los PDFs.
    """
    global CURRENT_FINAL_DF, CURRENT_TEMP_DIR
    if CURRENT_FINAL_DF is None or CURRENT_FINAL_DF.empty:
        return "No hay datos finales en memoria.", 400
    if not CURRENT_TEMP_DIR or not os.path.exists(CURRENT_TEMP_DIR):
        return "La carpeta temporal de PDFs no existe.", 400

    pdf_folder = os.path.join(CURRENT_TEMP_DIR, "pdfs")

    # 1) Convertir DF final a binario (Excel)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        CURRENT_FINAL_DF.to_excel(writer, index=False, sheet_name="ResultadoFinal")
    excel_buffer.seek(0)

    # 2) Crear ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Incluir el Excel final
        zf.writestr("ResultadoFinal.xlsx", excel_buffer.read())
        excel_buffer.seek(0)

        # Incluir PDFs
        if os.path.exists(pdf_folder):
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    with open(pdf_path, "rb") as pf:
                        pdf_bytes = pf.read()
                    zf.writestr(f"pdfs/{filename}", pdf_bytes)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="FinalMasPDFs.zip",
        mimetype="application/zip"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5000)
