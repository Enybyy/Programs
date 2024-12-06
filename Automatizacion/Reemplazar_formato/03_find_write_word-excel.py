# IMPORTAR LIBRERIAS
import time
from docx import Document
from functions.buscar_excel_02 import read_excel_data

start_time = time.time()

# Guardar el tiempo de inicio

print("INICIANDO...")

# ABRIR .DOCX
doc = Document('data/db_base/formato.docx')

print("ACCEDIENDO A DB...\n")

# ==========================EXCEL=============================== #

# READ EXCEL
archivo_excel = 'data/db_base/Format_contrato.xlsx'
columnas_requeridas = ['EMBAJADOR', 'N° DOC', 'DIRECCION', 'DISTRITO', 'CIUDAD',
                       'CAMPAÑA', 'DURACIÓN', 'FECHA DE INICIO', 'FECHA DE FIN', 'REMUNERACIÓN']
lista, time_01 = read_excel_data(archivo_excel, columnas_requeridas)
# print(lista)
# ==========================EXCEL=============================== #

# INGRESAR DATOS A CAMBIAR
number_doc = int(input(
    "INGRESA EL NÚMERO DE DOCUMENTOS QUE DESEA MODIFICAR Y GENERAR: "))

print("========= GENERANDO DOCUMENTOS =========\n")

# INICIAR LOOP
for l in list(range(number_doc)):

    # RECORRIENDO "list" PARA CAMBIAR DATOS
    name = lista[l][0]
    id = str(lista[l][1])
    address = lista[l][2]
    district = lista[l][3]
    province = lista[l][4]
    campaign = lista[l][5]
    days = str(lista[l][6])
    start_date = str(lista[l][7])
    end_date = str(lista[l][8])
    remuneration = str(lista[l][9])
    
    # Conversión de fecha para que salga como 'DD/MM/YYYY'
    start_date = lista[l][7].strftime('%d/%m/%Y')  # Formato: 10/12/2024
    end_date = lista[l][8].strftime('%d/%m/%Y')    # Formato: 10/12/2024


    # RECORRER CADA PARRAFO DEL DOC
    for text in doc.paragraphs:

        # CREAR LISTA text GUARDAR LOS runs FORMATEADOS
        formatted_runs = []

        # RECORRER CADA run EN EL PARRAFO
        for run in text.runs:
            # CONSERVAR EL PARRAFO OROGINAL DEL run
            formatted_run = run._element
            formatted_runs.append(formatted_run)

        if "CONTRATO" in run.text:
            print(f"Documento {l+1}° .DOCX GENERADO")
        # ELIMINAR DE LA CADENA "[NAME]" DEL PARRAFO
        text.clear()  # LIMPIAR EL CONTENIDO ORIGINAL DEL PARRAFO
        for run in formatted_runs:
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[NAME]"
            if "[NAME]" in run.text:
                text.add_run(name).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[ID]" in run.text:
                text.add_run(id).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[ADDRESS]" in run.text:
                text.add_run(address).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[DISTRICT]" in run.text:
                text.add_run(district).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[PROVINCE]" in run.text:
                text.add_run(province).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[CAMPAIGN]" in run.text:
                text.add_run(campaign).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[DAYS]" in run.text:
                text.add_run(days).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[FECHA]"
            elif "[START_DATE]" in run.text:
                text.add_run(start_date).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[END_DATE]" in run.text:
                text.add_run(end_date).bold = True
            # AGREGAR EL TEXTO PREDEFINIDO SOBRE LA POSICIÓN DE "[ID]"
            elif "[REMUNERATION]" in run.text:
                text.add_run(remuneration).bold = True
            else:
                # AGREGAR EL run ORIGINAL AL PÁRRAFO
                text._element.append(run)

    # GUARDAR DOC MODIFICADO
    try:
        doc.save(
            f'data/doc_generado/{name}.docx')
        print(f"Documento {name}.docx generado correctamente.")
    except Exception as e:
        print(f"Error al guardar el documento: {e}")

    print(
        f"""
        El texto '[NAME]' ha reemplzado por {name}.
        El texto '[ID]' ha reemplzado por {id}.
        El texto '[ADDRESS]' ha reemplzado por {address}.
        El texto '[DISTRICT]' ha reemplzado por {district}.
        El texto '[PROVINCE]' ha reemplzado por {province}.
        El texto '[CAMPAIGN]' ha reemplzado por {campaign}.
        El texto '[DAYS]' ha reemplzado por {days}.
        El texto '[START_DATE]' ha reemplzado por {start_date}.
        El texto '[END_DATE]' ha reemplzado por {end_date}.
        El texto '[REMUNERATION]' ha reemplzado por {remuneration}.
        """)
try:
    print("¡HECHO!")
except Exception as e:
    print(f"Error al guardar el documento: {e}")


# Tu código aquí

# Guardar el tiempo de finalización
end_time = time.time()

# Calcular la diferencia de tiempo en segundos
elapsed_time = end_time - start_time + time_01

# Imprimir el tiempo transcurrido en segundos
print(f"Tiempo transcurrido: {round(elapsed_time, 1)} segundos")
