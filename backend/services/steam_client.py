import requests
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

class SteamAPIClient:
    def __init__(self):
        self.api_key = os.getenv("STEAM_API_KEY")
        self.base_url = "https://api.steampowered.com"

    def obtener_biblioteca_usuario(self, steam_id: str) -> list:
        """
        Consulta la API oficial de Steam y devuelve una lista de AppIDs 
        que pertenecen al usuario.
        """
        if not self.api_key:
            raise ValueError("ERROR CRÍTICO: La API Key de Steam no está configurada.")

        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
        
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": False # Solo necesitamos el ID numérico para cruzar con nuestro CSV
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 401 or response.status_code == 403:
                 raise Exception("Acceso denegado. Verifica que tu API Key de Steam sea válida.")
            elif response.status_code != 200:
                raise Exception(f"Error en los servidores de Steam: Código {response.status_code}")

            data = response.json()
            
            # Validaciones de visibilidad del perfil
            if "response" not in data:
                raise Exception("Respuesta inválida de Steam.")
            
            if "games" not in data["response"]:
                # Si el perfil es privado, Steam devuelve "response: {}" vacío.
                raise Exception("El perfil de Steam es privado o no tiene juegos.")

            # Extraemos únicamente la lista de números (AppIDs)
            lista_appids = [juego["appid"] for juego in data["response"]["games"]]
            print(f"Éxito: Se recuperaron {len(lista_appids)} juegos del perfil {steam_id}")
            
            return lista_appids

        except requests.exceptions.RequestException as e:
             raise Exception(f"Falla de conexión al intentar contactar a Steam: {str(e)}")