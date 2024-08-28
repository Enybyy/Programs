Conversor de Imágenes WebP a PNG
Este proyecto es una aplicación sencilla para convertir imágenes en formato WebP a PNG utilizando Python y Tkinter. La conversión es realizada por la biblioteca Pillow y la interfaz gráfica está construida con Tkinter.

Descripción:
La aplicación permite seleccionar un directorio que contenga imágenes en formato WebP y convertirlas todas a formato PNG. El directorio de salida se crea automáticamente si no existe.

Requisitos:
Para ejecutar este proyecto, necesitas tener instaladas las siguientes bibliotecas de Python:

Pillow: Biblioteca para manejar la conversión de imágenes. Se basa en PIL (Python Imaging Library) y proporciona funcionalidades para abrir, manipular y guardar imágenes en varios formatos.
tkinter: Biblioteca para la creación de interfaces gráficas de usuario (GUI). Normalmente viene preinstalada con Python, pero en algunas distribuciones puede requerir instalación adicional.
Instalación de Dependencias

Puedes instalar Pillow utilizando pip:

pip install pillow

tkinter: En la mayoría de las instalaciones de Python, tkinter ya está incluido. Si no está disponible, consulta la documentación de tu distribución de Python para instrucciones específicas sobre cómo instalarlo.

Uso
Ejecuta el script Python:

Para iniciar la aplicación, ejecuta el script Python:

python webp_to_png.py

Interfaz de Usuario:

Se abrirá una ventana con un botón llamado "Iniciar Conversión".
Haz clic en el botón para iniciar la conversión de imágenes. La aplicación buscará imágenes con la extensión .webp en el directorio de origen especificado y las convertirá a formato .png.
Los archivos convertidos se guardarán en el directorio de destino especificado.
Construcción del Ejecutable
Para construir un ejecutable .exe a partir del script Python, usa pyinstaller. Asegúrate de tener pyinstaller instalado:

pip install pyinstaller
Luego, ejecuta el siguiente comando en la raíz del proyecto:

pyinstaller --onefile --windowed --distpath exe --workpath exe\build --specpath exe webp_to_png.py
Esto generará un archivo ejecutable en la carpeta exe.