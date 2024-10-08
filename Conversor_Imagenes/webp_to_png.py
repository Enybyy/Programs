from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox, QComboBox
from PySide6.QtCore import Qt
import os
from PIL import Image
import sys

# Variables globales para las carpetas y los formatos de imagen
carpeta_origen = ""
carpeta_destino = ""
formato_origen = "WEBP"  # Formato de imagen por defecto
formato_destino = "PNG"  # Formato de imagen por defecto

# Función para convertir imágenes
def convertir_imagenes():
    global carpeta_origen, carpeta_destino, formato_origen, formato_destino
    
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

def ejecutar_conversion():
    try:
        convertir_imagenes()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Ocurrió un error: {e}")

def seleccionar_carpeta_origen():
    global carpeta_origen
    carpeta = QFileDialog.getExistingDirectory(None, "Seleccionar Carpeta de Origen")
    if carpeta:
        carpeta_origen = carpeta
        entrada_origen.setText(carpeta)

def seleccionar_carpeta_destino():
    global carpeta_destino
    carpeta = QFileDialog.getExistingDirectory(None, "Seleccionar Carpeta de Destino")
    if carpeta:
        carpeta_destino = carpeta
        entrada_destino.setText(carpeta)

def cambiar_formato_origen(index):
    global formato_origen
    formatos = ["WEBP", "JPG", "PNG", "JPEG", "BMP", "GIF"]
    formato_origen = formatos[index]

def cambiar_formato_destino(index):
    global formato_destino
    formatos = ["PNG", "JPG", "JPEG", "BMP", "GIF"]
    formato_destino = formatos[index]

# Crear la aplicación
app = QApplication(sys.argv)

# Crear la ventana principal
ventana = QMainWindow()
ventana.setWindowTitle("Conversor de Imágenes")

# Crear el widget central
widget_central = QWidget()
ventana.setCentralWidget(widget_central)

# Crear el layout principal
layout_principal = QVBoxLayout()

# Crear el layout para los campos de entrada y botones de carpetas
layout_carpetas = QVBoxLayout()

# Etiqueta y campo de entrada para la carpeta de origen
label_origen = QLabel("Carpeta de Origen:")
entrada_origen = QLabel()
boton_origen = QPushButton("Seleccionar Carpeta de Origen")
boton_origen.setFixedSize(300, 50)  # Tamaño del botón
boton_origen.setStyleSheet("font-size: 18px;")  # Tamaño del texto
boton_origen.clicked.connect(seleccionar_carpeta_origen)

# Etiqueta y campo de entrada para la carpeta de destino
label_destino = QLabel("Carpeta de Destino:")
entrada_destino = QLabel()
boton_destino = QPushButton("Seleccionar Carpeta de Destino")
boton_destino.setFixedSize(300, 50)  # Tamaño del botón
boton_destino.setStyleSheet("font-size: 18px;")  # Tamaño del texto
boton_destino.clicked.connect(seleccionar_carpeta_destino)

# Añadir widgets al layout de carpetas
layout_carpetas.addWidget(label_origen)
layout_carpetas.addWidget(entrada_origen)
layout_carpetas.addWidget(boton_origen)
layout_carpetas.addWidget(label_destino)
layout_carpetas.addWidget(entrada_destino)
layout_carpetas.addWidget(boton_destino)

# Crear el layout para los selectores de formato y el botón de conversión
layout_formato_conversion = QVBoxLayout()

# Crear el combo box para seleccionar el formato de origen
combo_formato_origen = QComboBox()
formatos_origen = ["WEBP", "JPG", "PNG", "JPEG", "BMP", "GIF"]
combo_formato_origen.addItems(formatos_origen)
combo_formato_origen.currentIndexChanged.connect(cambiar_formato_origen)

# Crear el combo box para seleccionar el formato de destino
combo_formato_destino = QComboBox()
formatos_destino = ["PNG", "JPG", "JPEG", "BMP", "GIF"]
combo_formato_destino.addItems(formatos_destino)
combo_formato_destino.currentIndexChanged.connect(cambiar_formato_destino)

# Botón para iniciar la conversión
boton_conversion = QPushButton("Iniciar Conversión")
boton_conversion.setFixedSize(300, 50)  # Tamaño del botón
boton_conversion.setStyleSheet("font-size: 18px;")  # Tamaño del texto
boton_conversion.clicked.connect(ejecutar_conversion)

# Añadir widgets al layout de formato y conversión
layout_formato_conversion.addWidget(QLabel("Convertir de:"))
layout_formato_conversion.addWidget(combo_formato_origen)
layout_formato_conversion.addWidget(QLabel("a:"))
layout_formato_conversion.addWidget(combo_formato_destino)
layout_formato_conversion.addWidget(boton_conversion)

# Añadir layouts al layout principal
layout_principal.addLayout(layout_carpetas)
layout_principal.addLayout(layout_formato_conversion)

# Configurar el widget central
widget_central.setLayout(layout_principal)

# Ajustar tamaño de la ventana
ventana.resize(600, 400)  # Ajusta a un formato rectangular más grande

# Mostrar la ventana
ventana.show()

# Ejecutar la aplicación
sys.exit(app.exec())
