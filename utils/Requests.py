"""
Requests.py
===========

Ce module contient la classe `Requests` facilitant l'envoi asynchrone de requêtes HTTP.

Dependencies:
    aiohttp: Pour envoyer des requêtes HTTP asynchrones.
    json: Pour manipuler les données au format JSON.
"""

# Imports standards
import asyncio
import json
from typing import Optional, Dict, Any

# Imports tiers
import aiohttp


class Requests:
    """Classe utilitaire pour faciliter l'envoi de requêtes HTTP asynchrones.

    Attributes:
        base_url (str): L'URL de base du serveur contenant l'API.
        headers (dict | None): Les en-têtes HTTP envoyés lors des requêtes.
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """Initialise une instance de la classe `Requests`.

        Args:
            base_url (str): L'URL du serveur contenant l'API.
            headers (dict | None): Optionnel. En-têtes HTTP par défaut pour les requêtes.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}

    async def _request(
        self,
        method: str,
        endpoint: str,
        progress_callback=None,
        **kwargs,
    ) -> Any:
        """Méthode interne générique pour gérer toutes les requêtes HTTP.

        Cette méthode ne doit pas être appelée directement, mais via les méthodes
        publiques (`get`, `post`, `put`, `delete`).

        Args:
            method (str): Méthode HTTP de la requête (GET, POST, PUT, DELETE).
            endpoint (str): Chemin de l'API à appeler.
            progress_callback (Callable | None): Fonction pour suivre la progression de la requête.
            **kwargs: Paramètres additionnels pour `aiohttp.request`.

        Returns:
            Any: Données retournées par le serveur (JSON ou texte brut).

        Raises:
            aiohttp.ClientResponseError: Si la requête échoue (statut HTTP 4xx/5xx).
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(method, url, **kwargs) as response:
                # Gestion des erreurs HTTP
                if not response.ok:
                    try:
                        text = await response.json()
                    except aiohttp.ContentTypeError:
                        text = await response.text()

                    message = text.get("detail") if isinstance(text, dict) else str(text)

                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        request_info=response.request_info,
                        history=response.history,
                        message=message,
                        headers=response.headers,
                    )

                # Gestion de la progression du téléchargement
                total = int(response.headers.get("content-length", 0))
                data = bytearray()
                downloaded = 0

                if total and progress_callback:
                    progress_callback(0)

                async for chunk in response.content.iter_chunked(1024):
                    data.extend(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        percentage = int(downloaded / total * 100)
                        progress_callback(percentage)
                    await asyncio.sleep(0)

                if progress_callback and total:
                    progress_callback(100)

                # Tentative de décodage JSON, sinon texte brut
                try:
                    return json.loads(data.decode())
                except (aiohttp.ContentTypeError, json.JSONDecodeError):
                    return data.decode()

    # -------------------------------------------------------------------
    # 🌐 Méthodes publiques pour chaque type de requête HTTP
    # -------------------------------------------------------------------

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        progress_callback=None,
    ) -> Any:
        """Envoie une requête HTTP GET.

        Args:
            endpoint (str): Chemin de l'API.
            params (dict | None): Paramètres de la requête.
            headers (dict | None): En-têtes HTTP personnalisés.
            progress_callback (Callable | None): Fonction de suivi de progression.

        Returns:
            Any: Réponse du serveur.
        """
        return await self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            progress_callback=progress_callback,
        )

    async def post(
        self,
        endpoint: str,
        json_data: Optional[dict] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        progress_callback=None,
    ) -> Any:
        """Envoie une requête HTTP POST.

        Args:
            endpoint (str): Chemin de l'API.
            json_data (dict | None): Corps de la requête au format JSON.
            data (dict | None): Corps de la requête au format `x-www-form-urlencoded`.
            headers (dict | None): En-têtes HTTP personnalisés.
            progress_callback (Callable | None): Fonction de suivi de progression.

        Returns:
            Any: Réponse du serveur.
        """
        return await self._request(
            "POST",
            endpoint,
            data=data,
            json=json_data,
            headers=headers,
            progress_callback=progress_callback,
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        progress_callback=None,
    ) -> Any:
        """Envoie une requête HTTP PUT.

        Args:
            endpoint (str): Chemin de l'API.
            json_data (dict | None): Corps de la requête au format JSON.
            headers (dict | None): En-têtes HTTP personnalisés.
            progress_callback (Callable | None): Fonction de suivi de progression.

        Returns:
            Any: Réponse du serveur.
        """
        return await self._request(
            "PUT",
            endpoint,
            json=json_data,
            headers=headers,
            progress_callback=progress_callback,
        )

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        progress_callback=None,
    ) -> Any:
        """Envoie une requête HTTP DELETE.

        Args:
            endpoint (str): Chemin de l'API.
            headers (dict | None): En-têtes HTTP personnalisés.
            progress_callback (Callable | None): Fonction de suivi de progression.

        Returns:
            Any: Réponse du serveur.
        """
        return await self._request(
            "DELETE",
            endpoint,
            headers=headers,
            progress_callback=progress_callback,
        )
