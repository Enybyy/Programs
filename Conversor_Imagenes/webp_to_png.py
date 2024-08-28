# Librerías importadas
import os
from PIL import Image
import tkinter as tk
from tkinter import messagebox

# Función para convertir imágenes
def convertir_imagenes():
    # Carpeta de origen y destino
    carpeta_origen = "../../../../../Pictures/Psychedelic Wallpapers (WEBP)"
    carpeta_destino = "../../../../../Pictures/Psychedelic Wallpapers (JPEG)"

    # Crear la carpeta de destino si no existe
    os.makedirs(carpeta_destino, exist_ok=True)

    # Convertir todas las imágenes .webp a .png
    for archivo in os.listdir(carpeta_origen):
        if archivo.endswith(".webp"):   
            ruta_completa = os.path.join(carpeta_origen, archivo)
            imagen = Image.open(ruta_completa)
            nombre_sin_extension = os.path.splitext(archivo)[0]
            imagen.save(os.path.join(carpeta_destino, f"{nombre_sin_extension}.png"), "PNG")

def ejecutar_conversion():
    try:
        convertir_imagenes()
        messagebox.showinfo("Éxito", "La conversión de imágenes se completó correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Crear la ventana principal
root = tk.Tk()
root.title("Conversor de Imágenes")

# Crear un botón
boton = tk.Button(root, text="Iniciar Conversión", command=ejecutar_conversion)
boton.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()

# Crear ejecutable '.exe'    -->     pyinstaller --onefile --windowed --distpath exe --workpath exe\build --specpath exe webp_to_png.py
