from decimal import Decimal, getcontext
import pandas as pd  # Importamos pandas para trabajar con tablas (DataFrames)
import math  # Importar la librería math para funciones matemáticas

# Configurar la precisión deseada para Decimal
getcontext().prec = 100  # Ajusta la precisión según sea necesario

# Función para convertir de DMS a grados decimales usando Decimal
def dms_a_grados(grados, minutos, segundos):
    grados_decimal = Decimal(grados)
    minutos_decimal = Decimal(minutos) / Decimal(60)
    segundos_decimal = Decimal(segundos) / Decimal(3600)
    return grados_decimal + minutos_decimal + segundos_decimal

# Función para convertir de grados decimales a DMS usando Decimal
def grados_a_dms(grados_decimales, decimales=6):
    grados = int(grados_decimales)
    minutos_decimales = (Decimal(grados_decimales) - Decimal(grados)) * Decimal(60)
    minutos = abs(int(minutos_decimales))
    segundos = abs((minutos_decimales - Decimal(minutos)) * Decimal(60))
    return f"{grados}°{minutos}'{round(segundos, decimales)}''"  # Ajusta los decimales según sea necesario

# Función para calcular el siguiente azimut con corrección de 180°
def calcular_azimut(azimut_anterior, angulo):
    azimut_anterior_decimal = Decimal(azimut_anterior)
    nuevo_azimut = azimut_anterior_decimal + angulo
    if nuevo_azimut >= 360:
        nuevo_azimut -= 360
    # Aplicar corrección de 180° si es necesario
    if nuevo_azimut > 180:
        nuevo_azimut -= 180
    else:
        nuevo_azimut += 180
    return nuevo_azimut

# Ingresar el número de vértices
n_vertices = int(input("Ingrese el número de vértices (ángulos): "))

# Preguntar sobre el instrumento utilizado y precisión
instrumento = input("Ingrese el instrumento utilizado (ej. Teodolito, Estación Total): ")
precision = Decimal(input(f"Ingrese la precisión del equipo {instrumento} en segundos (ej. 20): "))

# Convertir la precisión a grados usando Decimal
precision_grados = precision / Decimal(3600)  # Convertimos segundos a grados

# Crear un diccionario para almacenar los ángulos
angulos_campo = {}

# Ingresar los ángulos en DMS para cada vértice
for i in range(n_vertices):
    punto = input(f"\nIngrese el nombre del punto {i + 1} (ej. A, B, C): ")
    print(f"\nIngrese el ángulo en DMS para el punto {punto}:")
    grados = int(input("Grados: "))
    minutos = int(input("Minutos: "))
    segundos = Decimal(input("Segundos: "))
    angulos_campo[punto] = (grados, minutos, segundos)

# Convertimos los ángulos a grados decimales
angulos_decimales = {punto: dms_a_grados(*dms) for punto, dms in angulos_campo.items()}

# Suma teórica de los ángulos (n vértices de un polígono, n*180)
suma_teorica = (Decimal(n_vertices) - Decimal(2)) * Decimal(180)

# Suma de los ángulos medidos
suma_medida = sum(angulos_decimales.values())

# Cálculo del Error Máximo Permitido (EMP) usando Decimal
EMP = precision_grados * Decimal(math.sqrt(n_vertices))  # EMP = AP * sqrt(n)

# Diferencia entre la suma medida y la suma teórica
diferencia = abs(suma_teorica - suma_medida)

# Calcular la corrección angular
correccion_angular = diferencia / Decimal(n_vertices)

# Aplicar la corrección a cada ángulo medido
angulos_corregidos = {punto: grados_decimal + correccion_angular for punto, grados_decimal in angulos_decimales.items()}

# Convertimos la diferencia, EMP, y la suma medida a DMS para mostrar los resultados
diferencia_dms = grados_a_dms(diferencia)
EMP_dms = grados_a_dms(EMP)
suma_medida_dms = grados_a_dms(suma_medida)

# Convertimos los ángulos corregidos a DMS
angulos_corregidos_dms = {punto: grados_a_dms(angulo) for punto, angulo in angulos_corregidos.items()}

# Crear un DataFrame con los ángulos originales en formato DMS (limitado a 2 decimales para la tabla)
df_angulos = pd.DataFrame({
    'Punto': list(angulos_campo.keys()),
    'Ángulo (DMS)': [f"{dms[0]}°{dms[1]}'{round(dms[2], 2)}''" for dms in angulos_campo.values()],
    'Ángulo Corregido (DMS)': [angulos_corregidos_dms[punto] for punto in angulos_campo.keys()]
})

# Crear un DataFrame separado para los resultados generales (limitado a 2 decimales para la tabla)
df_resultados = pd.DataFrame({
    'Descripción': ['Suma Teórica', 'Suma Medida', 'Error de Cierre (EC)', 'Error Máximo Permitido (EMP)'],
    'Resultado en DMS': [grados_a_dms(suma_teorica, 2), grados_a_dms(suma_medida, 2), grados_a_dms(diferencia, 2), grados_a_dms(EMP, 2)]
})

# Mostrar la tabla de ángulos
print("\nTabla de Ángulos en DMS y Ángulos Corregidos:")
print(df_angulos.to_markdown())

# Mostrar la tabla de resultados generales
print("\nResultados Generales:")
print(df_resultados.to_markdown())

# Mostrar los resultados adicionales
print(f"\nInstrumento: {instrumento}")
print(f"Precisión del equipo: {precision}''")
print(f"Suma teórica: {suma_teorica}°")
print(f"Suma medida: {suma_medida_dms}")
print(f"Error de cierre (EC): {diferencia_dms}")
print(f"Error Máximo Permitido (EMP): {EMP_dms}")

# Verificación si está dentro del error permitido
if diferencia <= EMP:
    print("Los ángulos están dentro del error permitido.")
else:
    print("Los ángulos exceden el error permitido.")

# Cálculo de los azimuts comenzando desde el segundo ángulo
# Convertimos los ángulos corregidos a grados decimales para el cálculo de azimuts
angulos_corregidos_list = list(angulos_corregidos.values())

# Ingresar el azimut inicial
azimut_inicial = Decimal(input("Ingrese el azimut inicial en grados decimales (ej. 84): "))

# Crear una lista para almacenar los azimuts
azimuts = [azimut_inicial]  # Inicializamos con el azimut inicial

# Comenzamos desde el segundo ángulo
for angulo in angulos_corregidos_list[1:]:
    nuevo_azimut = calcular_azimut(azimuts[-1], angulo)
    azimuts.append(nuevo_azimut)

# Mostrar los resultados de azimut en DMS
for i, azimut in enumerate(azimuts):
    azimut_dms = grados_a_dms(azimut)
    print(f"Azimut del punto {i + 1}: {azimut_dms}")

# Verificación del azimut final con el azimut inicial
azimut_final = (azimuts[-1] + angulos_corregidos_list[0]) % 360
if azimut_final > 180:
    azimut_final -= 180
else:
    azimut_final += 180

# Mostrar los resultados finales
print(f"\nAzimut calculado del punto final: {grados_a_dms(azimuts[-1])}")
print(f"Azimut final corregido: {grados_a_dms(azimut_final)}")
print(f"Azimut inicial ingresado: {grados_a_dms(azimut_inicial)}")

# Verificar si el azimut final corregido coincide con el inicial
tolerancia = Decimal(0)  # Tolerancia en grados, ajusta según sea necesario
diferencia_final = abs(azimut_final - azimut_inicial)
if diferencia_final <= tolerancia:
    print(f"El azimut calculado del punto final coincide con el azimut inicial dentro de la tolerancia.")
else:
    print(f"El azimut calculado del punto final no coincide con el azimut inicial dentro de la tolerancia.")
