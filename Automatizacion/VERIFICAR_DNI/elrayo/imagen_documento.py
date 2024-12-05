import os
import shutil
import pandas as pd

# Paso 1: Cargar la base de datos original y crear una copia
df_original = pd.read_excel("elrayo/data/db_original/Base_Etna_2.12.24-1.xlsx", sheet_name="Base_Etna_2.12")
df_copia = df_original.copy()  # Crear una copia de la base

# Carpetas
carpeta_origen = "elrayo/data/docs_originales"  # Carpeta donde están los archivos
carpeta_destino = "elrayo/data/docs_validados"  # Carpeta para guardar los archivos coincidentes

# Crear la carpeta destino si no existe
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Paso 2: Separar los archivos en la nueva carpeta
for index, row in df_copia.iterrows():
    archivo = row["Imagen Documento"]  # Nombre del archivo en la columna
    archivo = archivo.replace("etna/", "").strip()  # Eliminar el prefijo "etna/" y aplicar strip
    ruta_origen = os.path.join(carpeta_origen, archivo)
    ruta_destino = os.path.join(carpeta_destino, archivo)

    if os.path.exists(ruta_origen):  # Verificar si el archivo existe en la carpeta origen
        shutil.copy(ruta_origen, ruta_destino)  # Copiar el archivo a la carpeta destino
        print(f"Archivo encontrado y copiado: {archivo}")
    else:
        print(f"Archivo no encontrado: {archivo}")

# Paso 3: Renombrar los archivos en la nueva carpeta y actualizar la base de datos
for index, row in df_copia.iterrows():
    archivo_original = row["Imagen Documento"]  # Nombre original del archivo
    archivo_original = archivo_original.replace("etna/", "").strip()  # Eliminar el prefijo "etna/" y aplicar strip
    ruta_archivo = os.path.join(carpeta_destino, archivo_original)

    if os.path.exists(ruta_archivo):
        # Obtener el nombre y apellido de la fila, aplicando strip para limpiar espacios
        nombre = row["Nombre"].strip()
        apellido = row["Apellido"].strip()

        # Determinar la extensión del archivo original
        _, extension = os.path.splitext(archivo_original)

        # Crear el nuevo nombre del archivo
        nuevo_nombre = f"{nombre} {apellido}{extension}"

        # Evitar conflictos de nombres
        nueva_ruta = os.path.join(carpeta_destino, nuevo_nombre)
        contador = 1
        while os.path.exists(nueva_ruta):  # Si el archivo ya existe, agregar un sufijo
            nuevo_nombre = f"{nombre} {apellido} ({contador}){extension}"
            nueva_ruta = os.path.join(carpeta_destino, nuevo_nombre)
            contador += 1

        # Renombrar el archivo
        os.rename(ruta_archivo, nueva_ruta)
        print(f"Archivo renombrado: {archivo_original} -> {nuevo_nombre}")

        # Actualizar la columna "Imagen Documento" en la base de datos
        df_copia.at[index, "Imagen Documento"] = nuevo_nombre
    else:
        print(f"Archivo no encontrado en carpeta destino: {archivo_original}")

# Paso 4: Exportar la base de datos corregida a un archivo Excel
archivo_salida = "elrayo/data/db_pruebas/Base_Corregida.xlsx"
df_copia.to_excel(archivo_salida, index=False)
print(f"Base corregida exportada a {archivo_salida}")
