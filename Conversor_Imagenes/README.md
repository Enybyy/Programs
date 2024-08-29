## Conversor de Imágenes WebP a PNG

Este proyecto es una aplicación sencilla para convertir imágenes en formato WebP a PNG utilizando Python y Tkinter. La conversión es realizada por la biblioteca Pillow y la interfaz gráfica está construida con Tkinter.

### Descripción

La aplicación permite seleccionar un directorio que contenga imágenes en formato WebP y convertirlas todas a formato PNG. El directorio de salida se crea automáticamente si no existe.

### Requisitos

Para ejecutar este proyecto, necesitas tener instaladas las siguientes bibliotecas de Python:

- **Pillow**: Biblioteca para manejar la conversión de imágenes. Se basa en PIL (Python Imaging Library) y proporciona funcionalidades para abrir, manipular y guardar imágenes en varios formatos.
- **tkinter**: Biblioteca para la creación de interfaces gráficas de usuario (GUI). Normalmente viene preinstalada con Python, pero en algunas distribuciones puede requerir instalación adicional.

### Instalación de Dependencias

1. **Pillow**: Puedes instalar Pillow utilizando pip:

    ```bash
    pip install pillow
    ```

2. **tkinter**: En la mayoría de las instalaciones de Python, tkinter ya está incluido. Si no está disponible, consulta la documentación de tu distribución de Python para instrucciones específicas sobre cómo instalarlo.

### Uso

1. **Ejecuta el script Python**: Para iniciar la aplicación, ejecuta el script Python:

    ```bash
    python webp_to_png.py
    ```

2. **Interfaz de Usuario**: Al ejecutar el script, se abrirá una ventana con un botón "Iniciar Conversión". Haz clic en el botón para iniciar la conversión de imágenes.

### Generar Ejecutable

Para generar un archivo ejecutable `.exe` a partir del script, utiliza PyInstaller con el siguiente comando:

```bash
pyinstaller --onefile --windowed --distpath exe --workpath exe\build --specpath exe webp_to_png.py
```
