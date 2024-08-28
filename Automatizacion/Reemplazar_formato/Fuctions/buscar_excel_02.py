import pandas as pd
import time


def read_excel_data(ruta_archivo_excel, columnas_requeridas):
    # Guardar el tiempo de inicio
    start_time = time.time()

    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo_excel, header=0)

    # Configuración para mostrar todas las columnas y alinear el texto a la izquierda
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # Seleccionar las columnas requeridas
    datos_seleccionados = df[columnas_requeridas]

    # Llenar celdas en blanco con un valor específico
    valor_a_llenar = 'NaN'
    datos_seleccionados.fillna(valor_a_llenar, inplace=True)

    # Convertir los datos seleccionados a una lista de listas (sin encabezados)
    data_list = datos_seleccionados.values.tolist()

    # Guardar el tiempo de finalización
    end_time = time.time()

    # Calcular la diferencia de tiempo en segundos
    elapsed_time = end_time - start_time
    time_01 = elapsed_time + 1

    # Retornar los datos seleccionados
    return data_list, time_01


# Ejemplo de uso de la función
archivo_excel = 'C:/Users/EVENTOS/Desktop/PROJECT_PYTHON/ARCHIVOS_LOCALES/Format_contrato.xlsx'
columnas_requeridas = ['EMBAJADOR', 'N° DOC', 'DIRECCION', 'DISTRITO', 'CIUDAD',
                       'CAMPAÑA', 'DURACIÓN', 'FECHA DE INICIO', 'FECHA DE FIN', 'REMUNERACIÓN']
lista = read_excel_data(archivo_excel, columnas_requeridas)
# print(lista)
# print(lista[0][0])
