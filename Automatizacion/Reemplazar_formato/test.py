import pandas as pd

# Leer el archivo Excel
df = pd.read_excel("data/db_base/3.2 IT - CORRESPONDENCIA - CONTRATO RH.xlsx", header=0, usecols=range(12), nrows=1581)

# Verificar si hay nombres repetidos en la columna 'EMBAJADOR'
duplicados = df[df['EMBAJADOR'].duplicated()]

# Mostrar las filas con nombres repetidos
if not duplicados.empty:
    print("Nombres repetidos:")
    print(duplicados)
else:
    print("No hay nombres repetidos.")

print(len(duplicados))