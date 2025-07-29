import requests
from typing import Any, Dict, Optional

class NiceClient:
    """Класс для упрощенного взаимодействия с сервером."""
    def __init__(self, server_address: str):
        self.base_url = server_address.rstrip("/")

    def connect(self, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Отправляет запрос к серверу, вызывая функцию по имени."""
        url = f"{self.base_url}/{function_name}"
        try:
            # Если есть позиционные аргументы, отправляем как GET
            if args:
                params = {f"arg{i}": arg for i, arg in enumerate(args)}
                response = requests.get(url, params=params)
            # Если есть именованные аргументы, отправляем как POST
            else:
                response = requests.post(url, json=kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}