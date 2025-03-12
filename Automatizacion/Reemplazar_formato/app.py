import os
import io
import pandas as pd
from flask import Flask, request, render_template_string, send_file, redirect, flash
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
    """ Reemplaza etiquetas en el texto de un párrafo """
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
            flash('Falta algún archivo.')
            return redirect(request.url)
        excel_file = request.files['excel_file']
        template_file = request.files['template_file']
        if excel_file.filename == '' or template_file.filename == '':
            flash('No se seleccionó alguno de los archivos.')
            return redirect(request.url)
        if not (allowed_file(excel_file.filename, 'xlsx') and allowed_file(template_file.filename, 'docx')):
            flash('Tipo de archivo no válido. Asegúrate de subir un archivo Excel (.xlsx) y una plantilla Word (.docx).')
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
        except Exception as e:
            flash(f'Error al leer el archivo Excel: {e}')
            return redirect(request.url)
        
        if 'FECHA DE INICIO' in df.columns:
            df['FECHA DE INICIO'] = pd.to_datetime(df['FECHA DE INICIO'], errors='coerce', dayfirst=True)
        if 'FECHA DE FIN' in df.columns:
            df['FECHA DE FIN'] = pd.to_datetime(df['FECHA DE FIN'], errors='coerce', dayfirst=True)
        
        # Iterar sobre cada registro para generar el documento personalizado
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
            for paragraph in doc.paragraphs:
                replace_text_in_paragraph(paragraph, replacements)
            for table in doc.tables:
                for row_table in table.rows:
                    for cell in row_table.cells:
                        for paragraph in cell.paragraphs:
                            replace_text_in_paragraph(paragraph, replacements)
            
            nombre_archivo = f"{row.get('NOMBRE', 'nombre')}_{row.get('APELLIDO', 'apellido').replace(' ', '_')}.docx"
            output_path = os.path.join(output_dir, nombre_archivo)
            doc.save(output_path)
        
        # Empaquetar los documentos generados en un archivo ZIP
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for foldername, subfolders, filenames in os.walk(output_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, output_dir)
                    zipf.write(filepath, arcname)
        zip_stream.seek(0)
        return send_file(zip_stream, as_attachment=True, download_name=f"contracts_{timestamp}.zip", mimetype='application/zip')
    
    # HTML con Bootstrap para una interfaz moderna
    html = '''
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <title>Automatización de Contratos</title>
    </head>
    <body>
      <div class="container mt-5">
        <h1 class="mb-4">Automatización de Contratos</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="alert alert-warning">
              {% for message in messages %}
                <p>{{ message }}</p>
              {% endfor %}
            </div>
          {% endif %}
        {% endwith %}
        <form method="post" enctype="multipart/form-data">
          <div class="mb-3">
            <label for="excel_file" class="form-label">Archivo Excel (.xlsx)</label>
            <input type="file" class="form-control" id="excel_file" name="excel_file" accept=".xlsx" required>
          </div>
          <div class="mb-3">
            <label for="template_file" class="form-label">Plantilla Word (.docx)</label>
            <input type="file" class="form-control" id="template_file" name="template_file" accept=".docx" required>
          </div>
          <button type="submit" class="btn btn-primary">Generar Contratos</button>
        </form>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
