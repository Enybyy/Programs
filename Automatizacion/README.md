# Script de Automatización para Generación de Documentos

Este proyecto consiste en un script de Python que automatiza la generación de documentos en formato .docx a partir de datos en un archivo Excel.

## Descripción

El script:
1. Lee datos desde un archivo Excel.
2. Reemplaza los marcadores de posición en una plantilla de documento .docx.
3. Guarda los documentos generados en una carpeta específica.

## Requisitos

- **docx**: Para manipular documentos .docx.
- **pandas**: Para leer el archivo Excel.

Instala las dependencias con:

```bash
pip install python-docx pandas
```


1. **Prepara los Archivos**

   Asegúrate de que tu archivo de plantilla y el archivo Excel estén en las rutas especificadas en el script.

2. **Ejecuta el Script**

   Ejecuta el script con el siguiente comando:

   ```bash
   python script_automatizacion.py
