from dotenv import load_dotenv
import os
from conection import ApisNetPe
print(os.getcwd())

# Cargar el archivo .env desde la carpeta tokens
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tokens", "tk1.env")
load_dotenv(dotenv_path)

def main(dni):
    # Leer el token desde las variables de entorno
    APIS_TOKEN = os.getenv("APIS_TOKEN")
    
    if not APIS_TOKEN:
        raise ValueError("El token de la API no está configurado en las variables de entorno.")

    
    # Crear una instancia de la clase ApisNetPe
    api_consultas = ApisNetPe(APIS_TOKEN)

    # Realizar consulta para el DNI y RUC
    n_dni = dni  # Reemplaza por un DNI real
    # n_ruc = ruc  # Reemplaza por un RUC real

    # Verificar el DNI
    # print("Consulta DNI:")
    result_dni = api_consultas.get_person(n_dni)
    if result_dni:
        print (result_dni )# print(result_dni)
    else:
        print("No se pudo obtener la información del DNI")

    # # Verificar el RUC
    # print("\nConsulta RUC:")
    # result_ruc = api_consultas.get_company(n_ruc)
    # if result_ruc:
    #     print(result_ruc)
    # else:
    #     print("No se pudo obtener la información del RUC")


if __name__ == "__main__":
    # Solicitar al usuario los valores de DNI y RUC
    dni = "76173899"
    # ruc = input("Ingresar número de RUC: ")

    # Llamar a la función main con los valores ingresados por el usuario
    main(dni)