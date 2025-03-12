import os
import io
import pandas as pd
from flask import Flask, request, render_template, send_file, redirect, flash
from docx import Document
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'  # Cambia esto por una clave segura en producción

# Carpetas de almacenamiento temporal
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'xlsx', 'docx'}

# Crear las carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename, ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == ext

def replace_text_in_paragraph(paragraph, replacements):
    """Reemplaza etiquetas en el texto de un párrafo."""
    for key, value in replacements.items():
        if key in paragraph.text:
            for run in paragraph.runs:
                if key in run.text:
                    run.text = run.text.replace(key, str(value))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validar que se hayan enviado ambos archivos
        if 'excel_file' not in request.files or 'template_file' not in request.files:
            flash('Falta algún archivo.', 'danger')
            return redirect(request.url)
        excel_file = request.files['excel_file']
        template_file = request.files['template_file']
        if excel_file.filename == '' or template_file.filename == '':
            flash('No se seleccionó alguno de los archivos.', 'danger')
            return redirect(request.url)
        if not (allowed_file(excel_file.filename, 'xlsx') and allowed_file(template_file.filename, 'docx')):
            flash('Tipo de archivo no válido. Asegúrate de subir un archivo Excel (.xlsx) y una plantilla Word (.docx).', 'danger')
            return redirect(request.url)
        
        # Guardar los archivos de forma segura
        excel_filename = secure_filename(excel_file.filename)
        template_filename = secure_filename(template_file.filename)
        excel_path = os.path.join(UPLOAD_FOLDER, excel_filename)
        template_path = os.path.join(UPLOAD_FOLDER, template_filename)
        excel_file.save(excel_path)
        template_file.save(template_path)
        
        # Crear un directorio de salida con timestamp para evitar colisiones
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(OUTPUT_FOLDER, f"output_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Leer el Excel y convertir las columnas de fechas
        try:
            df = pd.read_excel(excel_path, dtype=str)
            total_records = len(df)
            flash(f'Se han detectado {total_records} registros a procesar.', 'info')
        except Exception as e:
            flash(f'Error al leer el archivo Excel: {e}', 'danger')
            return redirect(request.url)
        
        if 'FECHA DE INICIO' in df.columns:
            df['FECHA DE INICIO'] = pd.to_datetime(df['FECHA DE INICIO'], errors='coerce', dayfirst=True)
        if 'FECHA DE FIN' in df.columns:
            df['FECHA DE FIN'] = pd.to_datetime(df['FECHA DE FIN'], errors='coerce', dayfirst=True)
        
        # Iterar sobre cada registro para generar el documento personalizado
        processed_files = 0
        for index, row in df.iterrows():
            doc = Document(template_path)
            fecha_inicio = row['FECHA DE INICIO'].strftime('%d/%m/%Y') if pd.notna(row.get('FECHA DE INICIO')) else ''
            fecha_fin = row['FECHA DE FIN'].strftime('%d/%m/%Y') if pd.notna(row.get('FECHA DE FIN')) else ''
            replacements = {
                '[NOMBRE]': row.get('NOMBRE', ''),
                '[APELLIDO]': row.get('APELLIDO', ''),
                '[DNI]': row.get('DNI', ''),
                '[UBICACION]': row.get('UBICACION', ''),
                '[CAMPAÑA]': row.get('CAMPAÑA', ''),
                '[FECHA DE INICIO]': fecha_inicio,
                '[FECHA DE FIN]': fecha_fin,
                '[SALARIO]': row.get('SALARIO', '')
            }
            # Reemplazo en párrafos
            for paragraph in doc.paragraphs:
                replace_text_in_paragraph(paragraph, replacements)
            # Reemplazo en tablas (si las hubiera)
            for table in doc.tables:
                for row_table in table.rows:
                    for cell in row_table.cells:
                        for paragraph in cell.paragraphs:
                            replace_text_in_paragraph(paragraph, replacements)
            
            nombre_archivo = f"{row.get('NOMBRE', 'nombre')}_{row.get('APELLIDO', 'apellido').replace(' ', '_')}.docx"
            output_path_file = os.path.join(output_dir, nombre_archivo)
            doc.save(output_path_file)
            processed_files += 1
        
        # Empaquetar los documentos generados en un archivo ZIP
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for foldername, subfolders, filenames in os.walk(output_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, output_dir)
                    zipf.write(filepath, arcname)
        zip_stream.seek(0)
        flash(f'Se han generado {processed_files} contratos con éxito.', 'success')
        return send_file(zip_stream, as_attachment=True, download_name=f"contratos_{timestamp}.zip", mimetype='application/zip')
    
    # Renderizamos la plantilla index.html
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
