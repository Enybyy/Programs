## Conversor de Imágenes Avanzado (1.3)

Este proyecto es una aplicación avanzada para convertir imágenes entre diferentes formatos utilizando Python y PySide6. La conversión es realizada por la biblioteca Pillow, mientras que la interfaz gráfica está construida con PySide6 para proporcionar una experiencia de usuario moderna y amigable.

### Descripción

La aplicación permite seleccionar un directorio de origen que contenga imágenes y convertirlas a un formato de destino elegido. Los formatos soportados incluyen WebP, JPG, PNG, JPEG, BMP y GIF. La interfaz gráfica permite seleccionar tanto la carpeta de origen como la de destino, así como elegir los formatos de imagen de origen y destino mediante menús desplegables.

### Mejoras

- **Interfaz de Usuario Mejorada**: La interfaz gráfica se ha actualizado para usar PySide6 en lugar de Tkinter, proporcionando un diseño más moderno y flexible. Los elementos de la interfaz ahora están centrados y ajustados automáticamente al tamaño de la ventana, ofreciendo una experiencia de usuario más intuitiva.
  
- **Selección de Formatos**: Se ha añadido la capacidad de seleccionar el formato de origen y el formato de destino desde menús desplegables, mejorando la flexibilidad de la conversión.

- **Manejo de Errores**: Se han mejorado los mensajes de error y las comprobaciones de validez para asegurar que la aplicación maneje situaciones de error de manera más robusta y amigable.

- **Optimización de Layout**: El diseño de la ventana se ha optimizado para adaptarse automáticamente al tamaño de la pantalla, asegurando que todos los elementos de la interfaz se ajusten adecuadamente sin necesidad de ajustes manuales.

### Requisitos

Para ejecutar este proyecto, necesitas tener instaladas las siguientes bibliotecas de Python:

- **Pillow**: Biblioteca para manejar la conversión de imágenes. Se basa en PIL (Python Imaging Library) y proporciona funcionalidades para abrir, manipular y guardar imágenes en varios formatos.
- **PySide6**: Biblioteca para la creación de interfaces gráficas de usuario (GUI) con una apariencia moderna y flexible.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

    ```python
    pip install pillow
    ```

2. **tkinter**: En la mayoría de las instalaciones de Python, tkinter ya está incluido. Si no está disponible, consulta la documentación de tu distribución de Python para instrucciones específicas sobre cómo instalarlo.

### Uso

1. **Ejecuta el script Python**: Para iniciar la aplicación, ejecuta el script Python:

    ```python
    python webp_to_png.py
    ```

2. **Interfaz de Usuario**: Al ejecutar el script, se abrirá una ventana con un botón "Iniciar Conversión". Haz clic en el botón para iniciar la conversión de imágenes.

### Generar Ejecutable

Para generar un archivo ejecutable `.exe` a partir del script, utiliza PyInstaller con el siguiente comando:

    
    pyinstaller --onefile --windowed --distpath exe --workpath exe\build --specpath exe webp_to_png.py
    

