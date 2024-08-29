# Script de Automatización para Generación de Documentos

Este proyecto automatiza la generación de documentos en formato .docx a partir de datos extraídos de un archivo Excel.

## Descripción

El script realiza las siguientes acciones:
1. Lee datos desde un archivo Excel.
2. Reemplaza los marcadores de posición en una plantilla de documento .docx con los datos extraídos.
3. Guarda los documentos generados en una carpeta específica.

## Requisitos

- **python-docx**: Para manipular documentos .docx.
- **pandas**: Para leer y procesar el archivo Excel.

Instala las dependencias con:

```bash
pip install python-docx pandas
```

## Uso

1. **Preparar Archivos**
   - **Archivo de plantilla (.docx)**: Asegúrate de que tu documento de plantilla contenga marcadores de posición como `[NAME]`, `[ID]`, `[ADDRESS]`, etc.
   - **Archivo Excel**: El archivo Excel debe tener las columnas requeridas, como `Nombre`, `ID`, `Dirección`, etc.

2. **Ejecutar el Script**
   - Abre una terminal y navega al directorio donde se encuentra el script.
   - Ejecuta el script con:

   ```bash
   python nombre_del_script.py
   ```

   3. **Ingresar Datos**
   - Cuando se te solicite, ingresa el número de documentos que deseas generar. El script utilizará los datos del archivo Excel para crear los documentos correspondientes.

4. **Verificar Resultados**
   - Los documentos generados se guardarán en la carpeta especificada con los nombres adecuados.

## Ejemplos de Código

### Leer Datos desde Excel

Para leer datos desde un archivo Excel y seleccionar las columnas necesarias:

```python
import pandas as pd

# Leer el archivo Excel
df = pd.read_excel('ruta/a/tu/archivo.xlsx')

# Seleccionar columnas necesarias
datos = df[['Nombre', 'ID', 'Dirección']].fillna('NaN').values.tolist()
```

### Marcadores de Posición en Documento .docx

Para reemplazar los marcadores de posición en la plantilla de documento .docx con los datos leídos:

1. **Abrir el Documento de Plantilla**
   - Utiliza la biblioteca `docx` para abrir el archivo .docx que sirve como plantilla.

2. **Reemplazar Marcadores de Posición**
   - Itera sobre los párrafos y los runs del documento para buscar y reemplazar los marcadores de posición (por ejemplo, `[NAME]`, `[ID]`) con los datos correspondientes.

   ```python
   from docx import Document

   # Abrir el documento de plantilla
   doc = Document('ruta/a/tu/plantilla.docx')

   # Reemplazar marcadores de posición
   for paragraph in doc.paragraphs:
       for run in paragraph.runs:
           if "[NAME]" in run.text:
               run.text = run.text.replace("[NAME]", "Juan Pérez")
           if "[ID]" in run.text:
               run.text = run.text.replace("[ID]", "123456")
           # Reemplaza otros marcadores de posición de manera similar
    ```

### Guardar el Documento Modificado

Después de reemplazar los marcadores de posición en el documento .docx, debes guardar el archivo con un nombre específico que refleje los datos incluidos. Esto asegura que cada documento generado sea único y fácil de identificar.

1. **Guardar el Documento con Nombre Específico**

   Utiliza el método `save()` de `docx` para guardar el documento modificado. Asegúrate de que el nombre del archivo incluya datos relevantes (como el nombre del embajador) para facilitar su identificación.

   ```python
   # Guardar el documento con un nombre específico
   doc.save('ruta/a/tu/carpeta/Juan_Perez.docx')
   ```

## Consistencia del Script

El script asegura la consistencia en la generación de documentos mediante varios mecanismos:

1. **Lectura Uniforme**: Extrae datos del archivo Excel seleccionando solo las columnas necesarias para el documento. Esto garantiza que solo se maneje la información relevante y precisa.

2. **Reemplazo Sistemático**: Cambia los marcadores de posición en la plantilla .docx con los datos específicos proporcionados. Esto asegura que cada documento contenga la información correcta en los lugares adecuados.

3. **Guardado Estructurado**: Guarda cada documento con un nombre basado en los datos de entrada, como el nombre del embajador. Esto facilita la organización y la identificación de los documentos generados.

El script está diseñado para ser eficiente, manteniendo la calidad y precisión de los documentos generados a través de un proceso estandarizado para manejar la entrada de datos y la creación de archivos.

## Licencia

Este proyecto está bajo la licencia NMS.
