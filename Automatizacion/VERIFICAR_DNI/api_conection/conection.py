import requests
import logging
from typing import Optional


class ApisNetPe:
    BASE_URL = "https://api.apis.net.pe"
    
    def __init__(self, token: str) -> None:
        # Inicializa la clase con el token proporcionado
        self.token = token

    def _get(self, path: str, params: dict):
        # Función interna para hacer la solicitud GET
        url = f"{self.BASE_URL}{path}"

        # Encabezados con el token de autenticación
        headers = {
            "Authorization": self.token,
            "Referer": "https://apis.net.pe/api-tipo-cambio.html"
        }

        try:
            # Hacer la solicitud GET a la API
            response = requests.get(url, headers=headers, params=params)

            # Verificar el código de estado de la respuesta
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 422:
                logging.warning(f"{response.url} - Parámetro inválido - NO SE ENCONTRÓ EL NÚMERO DE DNI SOLICITADO")
            elif response.status_code == 403:
                logging.warning(f"{response.url} - IP bloqueada")
            elif response.status_code == 429:
                logging.warning(f"{response.url} - Demasiadas solicitudes")
            elif response.status_code == 401:
                logging.warning(f"{response.url} - Token inválido o limitado")
            else:
                logging.warning(f"{response.url} - Error del servidor status_code={response.status_code}")

        except requests.exceptions.RequestException as e:
            # Si hay un error al hacer la solicitud, lo capturamos
            logging.error(f"Error al realizar la solicitud a {url}: {str(e)}")

        # Si algo falla, devolvemos None
        return None

    # Métodos de consulta para DNI y RUC
    def get_person(self, dni: str) -> Optional[dict]:
        """Consulta información de una persona por su DNI"""
        return self._get("/v2/reniec/dni", {"numero": dni})

    def get_company(self, ruc: str) -> Optional[dict]:
        """Consulta información de una empresa por su RUC"""
        return self._get("/v2/sunat/ruc", {"numero": ruc})
