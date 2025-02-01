from flask import Flask, render_template, request, redirect, url_for, send_file, session, Response, jsonify
import os
import io
import zipfile
import tempfile
import logging
import pandas as pd
import shutil
import threading
import queue
import base64
from io import StringIO
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

# Importación de funciones propias
from utils import load_config
from validate_data import validate_data
from extract_data import extract_data_from_validated
from fill_data import process_and_fill_data

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'clave-segura-desarrollo')
app.config['PERMANENT_SESSION_LIFETIME'] = 900  # 15 minutos

# --- VARIABLES GLOBALES PARA LOGS Y ESTADO DEL PROCESO ---
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """Manejador de logs que coloca los mensajes en una cola para ser enviados en tiempo real."""
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

# Configurar logging para que además de lo que ya haces, se envíen los logs a la cola.
queue_handler = QueueHandler()
queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(queue_handler)
logging.getLogger().setLevel(logging.INFO)

# Configurar logging a consola (si no se configura antes)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Variables globales para el estado del proceso y para almacenar resultados
process_status = {'finished': False, 'error': None}  # Se actualizará en el proceso en background
PROCESS_RESULT = {}  # Almacenará los datos que se inyectarán en la sesión para la descarga

# --- FUNCIONES AUXILIARES ---
def cleanup_all_temp_files():
    """Elimina TODOS los directorios temporales antiguos."""
    try:
        temp_parent_dir = app.instance_path
        if os.path.exists(temp_parent_dir):
            dirs_removed = 0
            for dir_name in os.listdir(temp_parent_dir):
                if dir_name.startswith("pdf_extract_"):
                    dir_path = os.path.join(temp_parent_dir, dir_name)
                    shutil.rmtree(dir_path, ignore_errors=True)
                    dirs_removed += 1
            logging.info(f"ℹ️ Limpieza temporal completada. Directorios eliminados: {dirs_removed}")
    except Exception as e:
        logging.error(f"❌ Error crítico en limpieza general: {str(e)}", exc_info=True)

# --- RUTAS PARA STREAMING DE LOGS (SSE) ---
@app.route('/logs')
def stream_logs():
    def generate():
        while True:
            # Bloquea hasta obtener un log; si se desea timeout se puede agregar try/except
            log_entry = log_queue.get()
            # Se envía cada log con el formato SSE
            yield f"data: {log_entry}\n\n"
    return Response(generate(), mimetype='text/event-stream')

# --- RUTAS PRINCIPALES ---
@app.route("/")
def index():
    logging.info("ℹ️ Usuario accedió a la página principal")
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_process():
    logging.info("ℹ️ Se recibió solicitud para iniciar proceso")

    # Guardar archivos subidos en archivos temporales
    form_file = request.files.get("form_data_file")
    local_file = request.files.get("local_db_file")
    temp_files = []  # Para llevar registro de los archivos y poder eliminarlos en el background

    if form_file and form_file.filename:
        temp_form = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        form_file.save(temp_form.name)
        form_data_path = temp_form.name
        temp_files.append(form_data_path)
        logging.info(f"📄 Archivo de FORM Data guardado: {form_file.filename} ({os.path.getsize(temp_form.name)} bytes)")
    else:
        form_data_path = None

    if local_file and local_file.filename:
        temp_local = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        local_file.save(temp_local.name)
        local_db_path = temp_local.name
        temp_files.append(local_db_path)
        logging.info(f"📂 Archivo de Base Local guardado: {local_file.filename} ({os.path.getsize(temp_local.name)} bytes)")
    else:
        logging.error("❌ No se proporcionó archivo de Base Local")
        return "Archivo de Base Local es obligatorio", 400

    # Reiniciar variables globales para un nuevo proceso
    global process_status, PROCESS_RESULT
    process_status = {'finished': False, 'error': None}
    PROCESS_RESULT = {}

    logging.info("ℹ️ Archivos subidos guardados temporalmente. Se iniciará el proceso en segundo plano.")

    # Iniciar el proceso en un hilo separado, pasando las rutas de los archivos
    thread = threading.Thread(target=background_process_main, args=(form_data_path, local_db_path, temp_files))
    thread.start()

    # Retornar una plantilla intermedia que mostrará los logs en tiempo real
    return render_template("processing.html")

def background_process_main(form_data_path, local_db_path, temp_files):
    """
    Función que ejecuta el proceso principal en segundo plano.
    Se deben usar contextos de aplicación para acceder a variables de Flask.
    """
    with app.app_context():
        try:
            logging.info("\n\n== 🚀 INICIO DE PROCESO PRINCIPAL ==")
            # Limpieza de archivos temporales anteriores
            cleanup_all_temp_files()
            logging.info("ℹ️ Sesiones y archivos temporales anteriores eliminados")

            # Manejo de credenciales
            encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not encoded_credentials:
                logging.critical("❌ Error crítico: Credenciales de Google no configuradas")
                process_status['error'] = "Error: Configuración de Google incompleta"
                process_status['finished'] = True
                return

            try:
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_file:
                    temp_file.write(decoded_credentials)
                    service_account_file = temp_file.name
                logging.info("✅ Credenciales de Google decodificadas correctamente")
            except Exception as e:
                logging.error(f"❌ Error decodificando credenciales: {str(e)}", exc_info=True)
                process_status['error'] = "Error procesando credenciales"
                process_status['finished'] = True
                return

            # Validar credenciales con Google Drive
            try:
                load_config(service_account_file)
                logging.info("✅ Credenciales validadas con Google Drive")
            except DefaultCredentialsError as e:
                logging.critical(f"❌ Credenciales inválidas: {str(e)}")
                process_status['error'] = "Credenciales de Google inválidas"
                process_status['finished'] = True
                return

            # Validación de datos
            logging.info("🔍 Iniciando validación de datos...")
            df_val = validate_data(form_data_path, local_db_path)
            matches = df_val['Coincide'].sum()
            logging.info(f"✅ Validación completada. Coincidencias encontradas: {matches}/{len(df_val)}")

            # Extracción de PDFs desde Google Drive
            logging.info("📥 Descargando PDFs desde Google Drive...")
            tempdir = extract_data_from_validated(service_account_file, df_val)
            text_folder = os.path.join(tempdir, "extracted_text")
            logging.info(f"📦 PDFs almacenados en: {tempdir}")

            # Procesamiento final
            logging.info("🔄 Generando datos finales...")
            df_final = process_and_fill_data(df_val, text_folder, local_db_path)
            logging.info(f"🎉 Datos finales generados. Registros procesados: {len(df_final)}")

            # Almacenar resultados en la variable global (para luego inyectarlos en la sesión)
            global PROCESS_RESULT
            PROCESS_RESULT = {
                'validated_df': df_val.to_json(),
                'final_df': df_final.to_json(),
                'temp_dir': tempdir,
                'service_account_file': service_account_file
            }
            logging.info("💾 Datos del proceso guardados correctamente")

        except HttpError as e:
            logging.error(f"❌ Error de Google Drive: {str(e)}", exc_info=True)
            process_status['error'] = f"Error en Google Drive: {e}"
        except Exception as e:
            logging.critical(f"❌ Error fatal en el proceso principal: {str(e)}", exc_info=True)
            process_status['error'] = f"Error inesperado: {e}"
        finally:
            # Limpiar archivos temporales de carga
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
            logging.info("🧹 Archivos temporales de carga eliminados")
            process_status['finished'] = True
            logging.info("== 🏁 PROCESO FINALIZADO CON ÉXITO ==\n")

@app.route("/process_status")
def process_status_route():
    """Endpoint para consultar el estado del proceso (si terminó o si hubo error)."""
    return jsonify(process_status)

@app.route("/results")
def results():
    # Si aún no se procesaron los datos, redirigir a la página principal
    if not PROCESS_RESULT:
        logging.warning("⚠️ Intento de acceso a resultados sin datos procesados")
        return redirect(url_for("index"))
    # Inyectar en la sesión los datos del proceso (para mantener la compatibilidad con las descargas)
    session['validated_df'] = PROCESS_RESULT.get('validated_df')
    session['final_df'] = PROCESS_RESULT.get('final_df')
    session['temp_dir'] = PROCESS_RESULT.get('temp_dir')
    session['service_account_file'] = PROCESS_RESULT.get('service_account_file')
    logging.info("ℹ️ Usuario visualizando resultados")
    return render_template("results.html")

# --- RUTAS PARA DESCARGA DE ARCHIVOS ---
@app.route("/download-validated")
def download_validated():
    logging.info("📥 Solicitud de descarga de datos validados")
    if 'validated_df' not in session:
        logging.warning("⚠️ Intento de descarga sin datos validados")
        return "Datos no disponibles", 400
    
    try:
        df = pd.read_json(StringIO(session['validated_df']))
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        logging.info(f"✅ Archivo validado generado: {len(df)} registros")
        return send_file(
            output,
            as_attachment=True,
            download_name="DatosValidados.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"❌ Error generando DatosValidados: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-final")
def download_final():
    logging.info("📥 Solicitud de descarga de resultados finales")
    if 'final_df' not in session:
        logging.warning("⚠️ Intento de descarga sin datos finales")
        return "Datos no disponibles", 400
    
    try:
        df = pd.read_json(StringIO(session['final_df']))
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        logging.info(f"✅ Archivo final generado: {len(df)} registros")
        return send_file(
            output,
            as_attachment=True,
            download_name="ResultadoFinal.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging.error(f"❌ Error generando ResultadoFinal: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-final-plus-pdfs")
def download_final_plus_pdfs():
    logging.info("📦 Solicitud de paquete completo (datos + PDFs)")
    if 'final_df' not in session or 'validated_df' not in session or 'temp_dir' not in session:
        logging.warning("⚠️ Datos incompletos para descarga combo")
        return "No hay datos disponibles", 400

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Archivo final
            df_final = pd.read_json(StringIO(session['final_df']))
            excel_final_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_final_buffer, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            zf.writestr("ResultadoFinal.xlsx", excel_final_buffer.getvalue())
            logging.info("✅ Archivo final añadido al ZIP")

            # Archivo validado
            df_validated = pd.read_json(StringIO(session['validated_df']))
            excel_validated_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_validated_buffer, engine='openpyxl') as writer:
                df_validated.to_excel(writer, index=False)
            zf.writestr("DatosValidados.xlsx", excel_validated_buffer.getvalue())
            logging.info("✅ Archivo validado añadido al ZIP")

            # PDFs
            pdf_folder = os.path.join(session['temp_dir'], "pdfs")
            if os.path.exists(pdf_folder):
                pdf_count = 0
                for filename in os.listdir(pdf_folder):
                    if filename.lower().endswith(".pdf"):
                        pdf_path = os.path.join(pdf_folder, filename)
                        if os.path.getsize(pdf_path) > 0:
                            zf.write(pdf_path, f"pdfs/{filename}")
                            pdf_count += 1
                logging.info(f"📄 PDFs añadidos: {pdf_count} archivos")

        zip_buffer.seek(0)
        logging.info("✅ Paquete ZIP generado exitosamente")
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="ResultadoFinal_y_PDFs.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        logging.error(f"❌ Error generando paquete ZIP: {str(e)}", exc_info=True)
        return "Error generando archivo", 500

@app.route("/download-pdfs")
def download_pdfs():
    logging.info("📥 Solicitud de descarga de PDFs")
    if 'temp_dir' not in session:
        logging.warning("⚠️ Intento de descarga sin directorio temporal")
        return "No hay datos disponibles", 400

    pdf_folder = os.path.join(session['temp_dir'], "pdfs")
    if not os.path.exists(pdf_folder):
        logging.warning("⚠️ Directorio de PDFs no encontrado")
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
            logging.info(f"✅ PDFs empaquetados: {pdf_count} archivos")

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="PDFs_Descargados.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        logging.error(f"❌ Error generando ZIP de PDFs: {str(e)}", exc_info=True)
        return "Error en generación de archivo", 500

@app.route("/cleanup", methods=['POST'])
def cleanup():
    logging.info("🧹 Solicitud de limpieza general")
    try:
        cleanup_all_temp_files()
        session.clear()
        logging.info("✅ Limpieza completada exitosamente")
        return "Limpieza completa exitosa", 200
    except Exception as e:
        logging.error(f"❌ Error en limpieza: {str(e)}", exc_info=True)
        return "Error en limpieza", 500

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    app.run(debug=False, port=5000)
