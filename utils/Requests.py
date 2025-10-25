"""
Requests.py
===========

Module contenant la classe Requests afin de faciliter l'envoie des requêtes.

Dependencies:
    aiohttp: Pour envoyer des requêtes.
    json: Pour récupérer les données au format JSON
"""
import aiohttp
import asyncio
import json

from typing import Optional, Dict, Any


class Requests:
    """Classe permettant de faciliter l'envoie de requête.

    Attributes:
        base_url (str): l'URL du serveur contenant l'API
        headers (dict): l'entête envoyé lors des requêtes.
    """
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """Méthode de l'initialisation de la classe Requests.

        Args:
            base_url (str): l'URL du serveur contenant l'API
            headers (dict): Optionnel, l'entête envoyé lors des requêtes.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers

    """Client asynchrone générique pour gérer les requêtes HTTP"""
    async def _request(self, method: str, endpoint: str, progress_callback=None, **kwargs) -> Any:
        """Méthode interne qui gère toutes les requêtes HTTP

        Args:
            method (str): La méthode HTTP de la requête (GET, POST, ...).
            endpoint (str): Point final de l'URL de la requête.
            progress_callback: Optionnel, pour le suivi de la progression de la requête.
            **kwargs: Paramètres optionnels supplémentaires à la requête.

        Returns:
            Any: La réponse de la requête.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(method, url, **kwargs) as response:
                # Vérifie si la requête a échoué (ex: 404, 500, etc.)
                if not response.ok:
                    try:
                        text = await response.json()
                    except aiohttp.ContentTypeError:
                        text = await response.text()
                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        request_info=response.request_info,
                        history=response.history,
                        message=f"{text["detail"]}" if type(text) is dict else f"{text}",
                        headers=response.headers
                    )

                # Mise à jour de la progression de la requête
                total = int(response.headers.get("content-length", 0))
                data = bytearray()
                downloaded = 0

                if total and progress_callback:
                    progress_callback(0)

                async for chunk in response.content.iter_chunked(total):
                    data.extend(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        percentage = int(downloaded / total * 100)
                        progress_callback(percentage)
                    await asyncio.sleep(0)

                if progress_callback and total:
                    progress_callback(100)

                # Essaie de parser la réponse JSON, sinon renvoie le texte brut
                try:
                    return json.loads(data.decode())
                except aiohttp.ContentTypeError:
                    return data.decode()

    # ------------------------------
    # 🌐 Méthodes publiques
    # ------------------------------

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête GET

        Args:
            endpoint (str) : URL endpoint.
            params (dict) : Optionnel, si des paramètres doivent être ajoutés dans la requête.
            headers (dict) : Optionnel, par défaut None, l'entête de la requête (clé, etc).
            progress_callback: Optionnel, par défaut None, pour informer la progression de la requête.

        Returns:
            Any: La réponse de la requête.
        """
        return await self._request("GET", endpoint, params=params, headers=headers, progress_callback=progress_callback)

    async def post(self, endpoint: str, json: dict = None, data: Optional[Dict[str, Any]] = None, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête POST

        Args:
            endpoint (str) : URL endpoint.
            json (dict) : Optionnel, si un json doit être envoyé dans la requête.
            data (dict) : Optionnel, si des données doivent être envoyées dans la requête.
            headers (dict) : Optionnel, par défaut None, l'entête de la requête (clé, etc).
            progress_callback: Optionnel, par défaut None, pour informer la progression de la requête.

        Returns:
            Any: La réponse de la requête.
        """
        return await self._request("POST", endpoint, data=data, json=json, headers=headers, progress_callback=progress_callback)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête PUT

        Args:
            endpoint (str) : URL endpoint.
            json (dict) : Optionnel, si un json doit être envoyé dans la requête.
            headers (dict) : Optionnel, par défaut None, l'entête de la requête (clé, etc).
            progress_callback: Optionnel, par défaut None, pour informer la progression de la requête.

        Returns:
            Any: La réponse de la requête.
        """
        return await self._request("PUT", endpoint, json=json, headers=headers, progress_callback=progress_callback)

    async def delete(self, endpoint: str, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête DELETE

        Args:
            endpoint (str) : URL endpoint.
            headers (dict) : Optionnel, par défaut None, l'entête de la requête (clé, etc).
            progress_callback: Optionnel, par défaut None, pour informer la progression de la requête.

        Returns:
            Any: La réponse de la requête.
        """
        return await self._request("DELETE", endpoint, headers=headers, progress_callback=progress_callback)
