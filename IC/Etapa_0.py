from decimal import Decimal, getcontext
import pandas as pd

# Configurar la precisión deseada para Decimal
getcontext().prec = 100

def dms_a_grados(grados, minutos, segundos):
    """Convertir de grados, minutos y segundos a grados decimales usando Decimal."""
    grados_decimal = Decimal(grados)
    minutos_decimal = Decimal(minutos) / Decimal(60)
    segundos_decimal = Decimal(segundos) / Decimal(3600)
    return grados_decimal + minutos_decimal + segundos_decimal

def grados_a_dms(grados_decimales, decimales=6):
    """Convertir de grados decimales a grados, minutos y segundos en formato DMS."""
    grados = int(grados_decimales)
    minutos_decimal = (Decimal(grados_decimales) - Decimal(grados)) * Decimal(60)
    minutos = int(minutos_decimal)
    segundos = (minutos_decimal - Decimal(minutos)) * Decimal(60)
    return f"{grados}°{minutos}'{round(segundos, decimales)}''"

def calcular_azimut(azimut_anterior, angulo):
    """Calcular el siguiente azimut aplicando una corrección de 180° si es necesario."""
    nuevo_azimut = (Decimal(azimut_anterior) + Decimal(angulo)) % Decimal(360)
    # Ajuste con 180° si el nuevo azimut es menor o igual a 180°
    if nuevo_azimut <= Decimal(180):
        nuevo_azimut += Decimal(180)
    else:
        nuevo_azimut -= Decimal(180)
    return nuevo_azimut

def aplicar_correccion_angulos(angulos_decimales, suma_teorica, precision_grados):
    """Aplicar corrección a los ángulos medidos para que la suma sea igual a la suma teórica."""
    diferencia = abs(suma_teorica - sum(angulos_decimales.values()))
    correccion_angular = diferencia / Decimal(len(angulos_decimales))
    return {punto: angulo + correccion_angular for punto, angulo in angulos_decimales.items()}

def main():
    # Ingresar el número de vértices y detalles del instrumento
    n_vertices = int(input("Ingrese el número de vértices (ángulos): "))
    instrumento = input("Ingrese el instrumento utilizado (ej. Teodolito, Estación Total): ")
    precision = Decimal(input(f"Ingrese la precisión del equipo {instrumento} en segundos (ej. 20): "))

    # Convertir la precisión a grados usando Decimal
    precision_grados = precision / Decimal(3600)

    # Ingresar los ángulos en DMS para cada vértice
    angulos_campo = {}
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

    # Aplicar corrección angular
    angulos_corregidos = aplicar_correccion_angulos(angulos_decimales, suma_teorica, precision_grados)

    # Crear DataFrames para resultados
    df_angulos = pd.DataFrame({
        'Punto': list(angulos_campo.keys()),
        'Ángulo (DMS)': [f"{dms[0]}°{dms[1]}'{round(dms[2], 2)}''" for dms in angulos_campo.values()],
        'Ángulo Corregido (DMS)': [grados_a_dms(angulo) for angulo in angulos_corregidos.values()]
    })

    diferencia = abs(suma_teorica - sum(angulos_decimales.values()))
    EMP = precision_grados * Decimal(n_vertices).sqrt()

    df_resultados = pd.DataFrame({
        'Descripción': ['Suma Teórica', 'Suma Medida', 'Error de Cierre (EC)', 'Error Máximo Permitido (EMP)'],
        'Resultado en DMS': [grados_a_dms(suma_teorica), grados_a_dms(sum(angulos_decimales.values())), grados_a_dms(diferencia), grados_a_dms(EMP)]
    })

    # Mostrar resultados
    print("\nResultados Generales:")
    print(df_resultados.to_markdown())
    
    print("\nTabla de Ángulos en DMS y Ángulos Corregidos:")
    print(df_angulos.to_markdown())

    # Calcular los azimuts
    azimut_inicial = Decimal(input("Ingrese el azimut inicial en grados decimales (ej. 84): "))
    azimuts = [azimut_inicial]
    angulos_corregidos_list = list(angulos_corregidos.values())

    for angulo in angulos_corregidos_list[1:]:
        azimuts.append(calcular_azimut(azimuts[-1], angulo))

    print("\nAzimuts calculados:")
    for i, (punto, azimut) in enumerate(zip(list(angulos_campo.keys()), azimuts)):
        print(f"Azimut del punto {punto}: {grados_a_dms(azimut)}")

    # Verificación del azimut final
    azimut_final = (azimuts[-1] + angulos_corregidos_list[0]) % Decimal(360)
    # Ajustar el azimut final corregido con la misma lógica
    if azimut_final <= Decimal(180):
        azimut_final += Decimal(180)
    else:
        azimut_final -= Decimal(180)

    print(f"\nAzimut calculado del punto final: {grados_a_dms(azimuts[-1])}")
    print(f"Azimut final corregido: {grados_a_dms(azimut_final)}")
    print(f"Azimut inicial ingresado: {grados_a_dms(azimut_inicial)}")

    tolerancia = Decimal(0)  # Ajusta la tolerancia según sea necesario
    diferencia_final = abs(azimut_final - azimut_inicial)
    if diferencia_final <= tolerancia:
        print(f"El azimut calculado del punto final coincide con el azimut inicial dentro de la tolerancia.")
    else:
        print(f"El azimut calculado del punto final no coincide con el azimut inicial dentro de la tolerancia.")

if __name__ == "__main__":
    main()
