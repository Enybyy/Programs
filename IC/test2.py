from decimal import Decimal, getcontext
import math

# Establecer precisión de Decimal
getcontext().prec = 50

def calcular_desplazamientos(distancia, azimut):
    """Calcula los desplazamientos en X y Y (ΔX, ΔY) a partir de la distancia y el azimut"""
    azimut_rad = Decimal(azimut) * Decimal(math.pi) / Decimal(180)  # Convertir a radianes
    delta_x = distancia * Decimal(math.cos(azimut_rad))
    delta_y = distancia * Decimal(math.sin(azimut_rad))
    return delta_x, delta_y

def calcular_ajuste_distancias(distancias, azimuts):
    """Ajusta las distancias para corregir el error de cierre sin modificar los azimuts"""
    # Calcular el desplazamiento total en X y Y
    delta_x_total = Decimal(0)
    delta_y_total = Decimal(0)
    
    for i in range(len(distancias)):
        delta_x, delta_y = calcular_desplazamientos(distancias[i], azimuts[i])
        delta_x_total += delta_x
        delta_y_total += delta_y

    # Error de cierre en X y Y
    error_cierre_x = -delta_x_total
    error_cierre_y = -delta_y_total

    # Calcular perímetro total
    perimetro_total = sum(distancias)

    # Aplicar corrección proporcional a las distancias
    distancias_corregidas = []
    for i in range(len(distancias)):
        correccion_distancia = (distancias[i] / perimetro_total)
        # Distribuir el error de cierre proporcionalmente a las distancias
        correccion_x = correccion_distancia * error_cierre_x
        correccion_y = correccion_distancia * error_cierre_y
        correccion_total = Decimal(math.sqrt(correccion_x**2 + correccion_y**2))
        distancias_corregidas.append(distancias[i] + correccion_total)

    return distancias_corregidas

def main():
    # Datos de la poligonal (distancias y azimuts en grados decimales)
    distancias = [Decimal('10.0'), Decimal('10.0'), Decimal('10.0'), Decimal('9.0')]
    azimuts = [Decimal('0.0'), Decimal('90.0'), Decimal('180.0'), Decimal('270.0')]

    # Aplicar la corrección de cierre solo a las distancias
    distancias_corregidas = calcular_ajuste_distancias(distancias, azimuts)

    # Mostrar las distancias corregidas
    print("Distancias corregidas:")
    for i, distancia in enumerate(distancias_corregidas):
        print(f"Distancia {i + 1}: {distancia} m")

if __name__ == "__main__":
    main()
