import pandas as pd
import re
from docxtpl import DocxTemplate

def read_excel_data(ruta_archivo_excel, columnas_requeridas):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo_excel, header=0, usecols=range(12))
    
    # Limpiar los nombres de las columnas eliminando espacios en blanco
    df.columns = [col.strip() for col in df.columns]
    
    # Rellenar valores nulos con 'NaN'
    valor_a_llenar = 'NaN'
    df.fillna(valor_a_llenar, inplace=True)
    
    # Retornar los datos seleccionados
    return df[columnas_requeridas].values.tolist()

# Configuración inicial
archivo_excel = 'data/db_base/3.2 IT - CORRESPONDENCIA - CONTRATO RH.xlsx'
columnas_requeridas = ['EMBAJADOR', 'N° DOC', 'DIRECCION', 'DISTRITO', 'CIUDAD', 'CARGO',
                       'CAMPAÑA', 'DURACIÓN', 'FECHA DE INICIO', 'FECHA DE FIN', 'REMUNERACIÓN']

# Llamar a la función
lista = read_excel_data(archivo_excel, columnas_requeridas)

# Solicitar el número de documentos a generar
number_doc = int(input("INGRESA EL NÚMERO DE DOCUMENTOS QUE DESEA MODIFICAR Y GENERAR: "))

for l in range(number_doc):
    embajador = re.sub(r'[\\/*?:"<>|]', "", lista[l][0])  # Limpiar nombre
    id = str(lista[l][1])
    direccion = lista[l][2]
    distrito = lista[l][3]
    ciudad = lista[l][4]
    cargo = lista[l][5]
    campaña = lista[l][6]
    dias = str(lista[l][7])
    fecha_inicio = str(lista[l][8])
    fecha_fin = str(lista[l][9])
    remuneracion = str(lista[l][10])

    # Verificar si hay algún valor 'NaN' en los datos
    if 'NaN' in [embajador, id, direccion, distrito, ciudad, cargo, campaña, dias, fecha_inicio, fecha_fin, remuneracion]:
        # Si hay 'NaN', registrar como observado y guardar en la carpeta 'NaN'
        print(f"Documento {embajador}.docx OBSERVADO generado con valor NaN.")
        file_name = f'data/doc_generado/NaN/{embajador}-NaN.docx'
    else:
        # Si no hay 'NaN', generar normalmente el documento
        file_name = f'data/doc_generado/{embajador}.docx'

    # Crear el contexto con los valores extraídos
    context = {
        "EMBAJADOR": embajador,
        "ID": id,
        "DIRECCION": direccion,
        "DISTRITO": distrito,
        "CIUDAD": ciudad,
        "CARGO": cargo,
        "CAMPAÑA": campaña,
        "DURACION": dias,
        "FECHA_INICIO": fecha_inicio,
        "FECHA_FIN": fecha_fin,
        "REMUNERACION": remuneracion,
    }

    try:
        # Cargar plantilla y rellenar con datos
        doc = DocxTemplate('data/db_base/2.1 CONTRATO RH - FULL SHOPPER PUBLICIDAD.docx')
        doc.render(context)
        doc.save(file_name)
        print(f"Documento {file_name} generado correctamente.")
    except Exception as e:
        print(f"Error al generar {file_name}: {e}")
