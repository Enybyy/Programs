import os
from PIL import Image
from PySide6.QtWidgets import QMessageBox

def convertir_imagenes(carpeta_origen, carpeta_destino, formato_origen, formato_destino):
    # Asegurarse de que las carpetas estén definidas
    if not carpeta_origen or not carpeta_destino:
        QMessageBox.critical(None, "Error", "Las carpetas de origen o destino no están definidas.")
        return

    # Lista para verificar si se encontraron archivos
    archivos_convertidos = False
    
    # Convertir todas las imágenes al formato seleccionado
    for archivo in os.listdir(carpeta_origen):
        if archivo.lower().endswith(f".{formato_origen.lower()}"):  # Soporte para formato de origen
            archivos_convertidos = True
            ruta_completa = os.path.join(carpeta_origen, archivo)
            imagen = Image.open(ruta_completa)
            nombre_sin_extension = os.path.splitext(archivo)[0]
            imagen.save(os.path.join(carpeta_destino, f"{nombre_sin_extension}.{formato_destino.lower()}"), formato_destino)
    
    if archivos_convertidos:
        QMessageBox.information(None, "Éxito", "La conversión de imágenes se completó correctamente.")
    else:
        QMessageBox.information(None, "Sin Imágenes", f"No se encontraron imágenes con el formato {formato_origen} para convertir.")
