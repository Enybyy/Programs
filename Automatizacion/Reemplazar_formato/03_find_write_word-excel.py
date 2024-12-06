import pandas as pd
import time
import re
from docxtpl import DocxTemplate
from datetime import datetime

def read_excel_data(ruta_archivo_excel, columnas_requeridas):
    df = pd.read_excel(ruta_archivo_excel, header=0)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    valor_a_llenar = 'NaN'
    df.fillna(valor_a_llenar, inplace=True)
    return df[columnas_requeridas].values.tolist()

# Configuración inicial
archivo_excel = 'data/db_base/Format_contrato.xlsx'
columnas_requeridas = ['EMBAJADOR', 'N° DOC', 'DIRECCION', 'DISTRITO', 'CIUDAD',
                       'CAMPAÑA', 'DURACIÓN', 'FECHA DE INICIO', 'FECHA DE FIN', 'REMUNERACIÓN']
lista = read_excel_data(archivo_excel, columnas_requeridas)

number_doc = int(input("INGRESA EL NÚMERO DE DOCUMENTOS QUE DESEA MODIFICAR Y GENERAR: "))

for l in range(number_doc):
    name = re.sub(r'[\\/*?:"<>|]', "", lista[l][0])  # Limpiar nombre
    id = str(lista[l][1])
    address = lista[l][2]
    district = lista[l][3]
    province = lista[l][4]
    campaign = lista[l][5]
    days = str(lista[l][6])
    start_date = pd.to_datetime(lista[l][7], errors='coerce').strftime('%d/%m/%Y')
    end_date = pd.to_datetime(lista[l][8], errors='coerce').strftime('%d/%m/%Y')
    remuneration = str(lista[l][9])

    context = {
        "NAME": name,
        "ID": id,
        "ADDRESS": address,
        "DISTRICT": district,
        "PROVINCE": province,
        "CAMPAIGN": campaign,
        "DAYS": days,
        "START_DATE": start_date,
        "END_DATE": end_date,
        "REMUNERATION": remuneration,
    }

    try:
        doc = DocxTemplate('data/db_base/formato.docx')
        doc.render(context)
        doc.save(f'data/doc_generado/{name}.docx')
        print(f"Documento {name}.docx generado correctamente.")
    except Exception as e:
        print(f"Error al generar {name}.docx: {e}")
