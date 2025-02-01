from flask import Flask, render_template, request, redirect, url_for, send_file, session, Response
import os
import io
import zipfile
import tempfile
import logging
import pandas as pd
import shutil
import base64
from io import StringIO
from utils import load_config
from validate_data import validate_data
from extract_data import extract_data_from_validated
from fill_data import process_and_fill_data
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'clave-segura-desarrollo')
app.config['PERMANENT_SESSION_LIFETIME'] = 900  # 15 minutos

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def cleanup_all_temp_files():
    """
    Elimina TODOS los directorios temporales antiguos.
    """
    try:
        temp_parent_dir = app.instance_path
        if os.path.exists(temp_parent_dir):
            dirs_removed = 0
            for dir_name in os.listdir(temp_parent_dir):
                if dir_name.startswith("pdf_extract_"):
                    dir_path = os.path.join(temp_parent_dir, dir_name)
                    shutil.rmtree(dir_path, ignore_errors=True)
                    dirs_removed += 1
            logging.info(f"ℹ️  [Limpieza] Archivos temporales eliminados: {dirs_removed}")
        else:
            logging.info("ℹ️  [Limpieza] No se encontró directorio de instancias para limpieza")
    except Exception as e:
        logging.error(f"❌ [Limpieza] Error al limpiar archivos temporales: {str(e)}", exc_info=True)

@app.route("/")
def index():
    logging.info("Página principal cargada")
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    logging.info("\n\n===============================================")
    logging.info("ℹ️  [Inicio] Iniciando el proceso principal")
    
    # Limpieza de archivos y sesiones previas
    cleanup_all_temp_files()
    session.clear()
    logging.info("ℹ️  [Sesión] Sesiones y archivos temporales previos eliminados")
    
    # Manejo de credenciales de Google
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not encoded_credentials:
        logging.critical("❌ [Credenciales] Error crítico: Credenciales de Google no configuradas")
        return "Error: Configuración de Google incompleta", 500

    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_file:
            temp_file.write(decoded_credentials)
            service_account_file = temp_file.name
        logging.info("✅ [Credenciales] Credenciales de Google decodificadas correctamente")
    except Exception as e:
        logging.error(f"❌ [Credenciales] Error al decodificar credenciales: {str(e)}", exc_info=True)
        return "Error procesando credenciales", 500

    try:
        load_config(service_account_file)
        logging.info("✅ [Credenciales] Credenciales validadas correctamente con Google Drive")
    except DefaultCredentialsError as e:
        logging.critical(f"❌ [Credenciales] Credenciales inválidas: {str(e)}")
        return "Credenciales de Google inválidas", 500

    # Procesamiento de archivos subidos
    form_file = request.files.get("form_data_file")
    local_file = request.files.get("local_db_file")
    temp_files = []
    try:
        logging.info("ℹ️  [Archivos] Procesando archivos de entrada")
        form_data_path = ""
        local_db_path = ""

        if form_file and form_file.filename:
            temp_form = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            form_file.save(temp_form.name)
            form_data_path = temp_form.name
            temp_files.append(temp_form.name)
            logging.info(f"✅ [Archivos] Archivo de formulario recibido: {form_file.filename}")

        if local_file and local_file.filename:
            temp_local = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            local_file.save(temp_local.name)
            local_db_path = temp_local.name
            temp_files.append(temp_local.name)
            logging.info(f"✅ [Archivos] Archivo de base local recibido: {local_file.filename}")

        # Validación de datos
        logging.info("ℹ️  [Validación] Iniciando validación de datos")
        df_val = validate_data(form_data_path, local_db_path)
        matches = df_val['Coincide'].sum() if not df_val.empty else 0
        logging.info(f"✅ [Validación] Datos validados. Coincidencias: {matches} de {len(df_val)}")

        # Descarga y extracción de PDFs
        logging.info("ℹ️  [PDF] Descargando PDFs desde Google Drive")
        tempdir = extract_data_from_validated(service_account_file, df_val)
        logging.info(f"✅ [PDF] PDFs y textos extraídos en: {tempdir}")

        # Procesamiento final
        logging.info("ℹ️  [Procesamiento] Generando datos finales")
        text_folder = os.path.join(tempdir, "extracted_text")
        df_final = process_and_fill_data(df_val, text_folder, local_db_path)
        logging.info(f"✅ [Procesamiento] Datos finales generados. Registros procesados: {len(df_final)}")

        # Almacenamiento en sesión
        session['validated_df'] = df_val.to_json()
        session['final_df'] = df_final.to_json()
        session['temp_dir'] = tempdir
        session['service_account_file'] = service_account_file

        # Almacenar resumen del proceso
        summary = {
            "observaciones": "Proceso completado con éxito.",
            "errores": "Ninguno",
            "total_validado": len(df_val),
            "total_final": len(df_final)
        }
        session['process_summary'] = summary

        logging.info("✅ [Sesión] Datos y resumen almacenados en sesión correctamente")
    except HttpError as e:
        logging.error(f"❌ [Google Drive] Error durante la comunicación con Google Drive: {str(e)}", exc_info=True)
        return f"Error en Google Drive: {e}", 500
    except Exception as e:
        logging.critical(f"❌ [Proceso] Error inesperado durante el proceso principal: {str(e)}", exc_info=True)
        return f"Error inesperado: {e}", 500
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.unlink(f)
        if 'service_account_file' in locals() and os.path.exists(service_account_file):
            os.unlink(service_account_file)
        logging.info("ℹ️  [Limpieza] Archivos temporales eliminados")
    
    logging.info("✅ [Finalización] Proceso principal finalizado con éxito")
    logging.info("===============================================\n")
    return redirect(url_for("results"))

@app.route("/results")
def results():
    if 'validated_df' not in session:
        logging.warning("⚠️  [Acceso] Intento de visualizar resultados sin sesión válida")
        return redirect(url_for("index"))
    logging.info("ℹ️  [Resultados] Usuario visualizando resultados")
    return render_template("results.html")

@app.route("/download-validated")
def download_validated():
    logging.info("ℹ️  [Descarga] Solicitud de descarga de datos validados")
    if 'validated_df' not in session:
        logging.warning("⚠️  [Descarga] No hay datos validados disponibles para descarga")
        return "Datos no disponibles", 400
    try:
        df = pd.read_json(StringIO(session['validated_df']))
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        logging.info(f"✅ [Descarga] Archivo de datos validados generado. Registros: {len(df)}")
        return send_file(
            output,
            as_attachment=True,
            download_name="DatosValidados.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"❌ [Descarga] Error al generar archivo de datos validados: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-final")
def download_final():
    logging.info("ℹ️  [Descarga] Solicitud de descarga de resultados finales")
    if 'final_df' not in session:
        logging.warning("⚠️  [Descarga] No hay datos finales disponibles para descarga")
        return "Datos no disponibles", 400
    try:
        df = pd.read_json(StringIO(session['final_df']))
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        logging.info(f"✅ [Descarga] Archivo de resultados finales generado. Registros: {len(df)}")
        return send_file(
            output,
            as_attachment=True,
            download_name="ResultadoFinal.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"❌ [Descarga] Error al generar archivo de resultados finales: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    logging.info("ℹ️  [Descarga] Solicitud de descarga de paquete completo (datos + PDFs)")
    if 'final_df' not in session or 'validated_df' not in session or 'temp_dir' not in session:
        logging.warning("⚠️  [Descarga] Datos incompletos para la descarga combinada")
        return "No hay datos disponibles", 400
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            df_final = pd.read_json(StringIO(session['final_df']))
            excel_final_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_final_buffer, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            zf.writestr("ResultadoFinal.xlsx", excel_final_buffer.getvalue())
            logging.info("✅ [ZIP] Archivo de resultados finales añadido")
            
            df_validated = pd.read_json(StringIO(session['validated_df']))
            excel_validated_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_validated_buffer, engine='openpyxl') as writer:
                df_validated.to_excel(writer, index=False)
            zf.writestr("DatosValidados.xlsx", excel_validated_buffer.getvalue())
            logging.info("✅ [ZIP] Archivo de datos validados añadido")
            
            pdf_folder = os.path.join(session['temp_dir'], "pdfs")
            if os.path.exists(pdf_folder):
                pdf_count = 0
                for filename in os.listdir(pdf_folder):
                    if filename.lower().endswith(".pdf"):
                        pdf_path = os.path.join(pdf_folder, filename)
                        if os.path.getsize(pdf_path) > 0:
                            zf.write(pdf_path, f"pdfs/{filename}")
                            pdf_count += 1
                logging.info(f"✅ [ZIP] PDFs añadidos al paquete: {pdf_count} archivo(s)")
        zip_buffer.seek(0)
        logging.info("✅ [ZIP] Paquete ZIP generado exitosamente")
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="ResultadoFinal_y_PDFs.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        logging.error(f"❌ [ZIP] Error al generar el paquete ZIP: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-pdfs")
def download_pdfs():
    logging.info("ℹ️  [Descarga] Solicitud de descarga de PDFs")
    if 'temp_dir' not in session:
        logging.warning("⚠️  [Descarga] Directorio temporal no disponible para descarga de PDFs")
        return "No hay datos disponibles", 400

    pdf_folder = os.path.join(session['temp_dir'], "pdfs")
    if not os.path.exists(pdf_folder):
        logging.warning("⚠️  [Descarga] Carpeta de PDFs no encontrada")
        return "No se encontraron PDFs para descargar", 404

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            pdf_count = 0
            for filename in os.listdir(pdf_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    if os.path.getsize(pdf_path) > 0:
                        zf.write(pdf_path, f"pdfs/{filename}")
                        pdf_count += 1
            logging.info(f"✅ [Descarga] ZIP de PDFs generado. Archivos incluidos: {pdf_count}")
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="PDFs_Descargados.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        logging.error(f"❌ [Descarga] Error al generar el ZIP de PDFs: {str(e)}", exc_info=True)
        return "Error en generación de archivo", 500

@app.route("/cleanup", methods=['POST'])
def cleanup():
    logging.info("ℹ️  [Limpieza] Solicitud de limpieza general recibida")
    try:
        cleanup_all_temp_files()
        session.clear()
        logging.info("✅ [Limpieza] Limpieza completada exitosamente")
        return "Limpieza completa exitosa", 200
    except Exception as e:
        logging.error(f"❌ [Limpieza] Error durante la limpieza: {str(e)}", exc_info=True)
        return "Error en limpieza", 500

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    logging.info("Servidor iniciado en el puerto 5000")
    app.run(debug=False, port=5000)
