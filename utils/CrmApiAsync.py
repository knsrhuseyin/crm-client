"""
CrmApiAsync.py
==============

Module client pour interagir avec l'API CRM de manière asynchrone.

Dependencies:
    json: Pour la manipulation des fichiers JSON.
    dotmap: Pour convertir les dictionnaires en objets avec accès par attribut.
    aiohttp: Pour gérer les exceptions HTTP via la classe Requests.
"""

import os
from typing import Optional, Dict, Any, Callable

from aiohttp import ClientResponseError, ClientConnectorDNSError
from dotmap import DotMap

from utils.Requests import Requests
from utils.utils import get_key_data_json


class CrmApiAsync(Requests):
    """Client asynchrone pour interagir avec l'API CRM.

    Hérite de Requests pour l'envoi de requêtes HTTP.

    Attributes:
        Ok (int): Code 200 si la requête réussit.
        ErrorDNS (int): Code 0 si le serveur est inaccessible.
        AccessTokenError (int): Code 400 si le token est expiré ou invalide.
        OtherError (int): Code 450 pour une erreur interne lors de la requête.
        ErrorNotFound (int): Code 500 pour une erreur externe non identifiée.
        auth_file (str): Chemin du fichier stockant les informations d'authentification.
        error (DotMap): Objet réutilisable pour stocker les erreurs DNS.
    """

    Ok: int = 200
    ErrorDNS: int = 0
    AccessTokenError: int = 400
    OtherError: int = 450
    ErrorNotFound: int = 500

    def __init__(
        self,
        base_url: str,
        auth_file: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialise le client CrmApiAsync.

        Args:
            base_url (str): URL de l'API.
            auth_file (str): Chemin du fichier stockant les informations d'auth.
            headers (Optional[Dict[str, str]]): En-têtes HTTP facultatifs.
        """
        super().__init__(base_url, headers)
        self.auth_file = auth_file
        self.error = DotMap()

    async def login(
        self,
        email: str,
        password: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """Se connecte à l'API et récupère l'access token.

        Args:
            email (str): Email utilisateur.
            password (str): Mot de passe.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Réponse de l'API ou erreur.
        """
        try:
            response = await self.post(
                "auth/token",
                data={"username": email, "password": password},
                progress_callback=progress_callback,
            )
            self.headers = {"Authorization": f"Bearer {response['access_token']}"}
            return response
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def create_user(
        self,
        name: str,
        first_name: str,
        email: str,
        telephone: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """Ajoute un utilisateur dans la base de données.

        Args:
            name (str): Nom.
            first_name (str): Prénom.
            email (str): Email.
            telephone (str): Téléphone.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Données de l'utilisateur ajouté ou erreur.
        """
        data = {
            "name": name,
            "first_name": first_name,
            "email": email,
            "telephone": telephone,
        }
        try:
            return await self.post(
                "crm/users/",
                json_data=data,
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def get_user(
        self, user_id: int, progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Récupère un utilisateur via son ID.

        Args:
            user_id (int): ID de l'utilisateur.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Données utilisateur ou erreur.
        """
        try:
            return await self.get(
                f"crm/users/{user_id}",
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def get_user_with_email(
        self, email: str, progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Récupère un utilisateur via son email.

        Args:
            email (str): Email de l'utilisateur.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Données utilisateur ou erreur.
        """
        try:
            return await self.get(
                f"crm/users/email/{email}",
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def update_user(
        self,
        user_id: int,
        modification: Dict[str, Any],
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """Met à jour les informations d'un utilisateur via son ID.

        Args:
            user_id (int): ID de l'utilisateur.
            modification (Dict[str, Any]): Nouvelles données de l'utilisateur.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Données mises à jour ou erreur.
        """
        new_data = {
            "name": modification["name"],
            "first_name": modification["first_name"],
            "email": modification["email"],
            "telephone": modification["telephone"],
        }
        try:
            return await self.put(
                f"crm/users/{user_id}",
                json_data=new_data,
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def delete_user(
        self, user_id: int, progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Supprime un utilisateur via son ID.

        Args:
            user_id (int): ID de l'utilisateur.
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Confirmation ou erreur.
        """
        try:
            return await self.delete(
                f"crm/users/{user_id}",
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def get_all_users(
        self, progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Récupère tous les utilisateurs.

        Args:
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Liste des utilisateurs ou erreur.
        """
        try:
            return await self.get(
                "crm/users/",
                headers=self.headers,
                progress_callback=progress_callback,
            )
        except ClientConnectorDNSError:
            self.error.err.message = "Not connected"
            return self.error
        except ClientResponseError as e:
            return {"err": e}

    async def get_current_user_access(
        self, progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Vérifie l'accès de l'utilisateur courant.

        Args:
            progress_callback (Callable[[int], None], optional): Fonction de suivi de progression.

        Returns:
            Dict[str, Any]: Données de l'utilisateur courant ou message d'erreur.
        """
        if self.headers:
            try:
                return await self.get(
                    "crm",
                    headers=self.headers,
                    progress_callback=progress_callback,
                )
            except ClientConnectorDNSError:
                self.error.err.message = "Not connected"
                return self.error
            except ClientResponseError as e:
                self.error.err.message = e
                return self.error
        else:
            token = get_key_data_json(self.auth_file, "access_token")
            if token:
                self.headers = {"Authorization": f"Bearer {token}"}
                return await self.get_current_user_access(progress_callback)
            else:
                if os.path.exists(self.auth_file):
                    os.remove(self.auth_file)
                self.error.err.message = "Could not verify credentials"
                return self.error

    async def verify_request(self, response: Dict[str, Any]) -> int:
        """Vérifie l'état de la requête effectuée.

        Args:
            response (Dict[str, Any]): Réponse de l'API.

        Returns:
            int: Code de statut défini par les attributs de la classe.
        """
        if "err" not in response:
            return self.Ok
        err = response.get("err")
        if hasattr(err, "message"):
            if err.message == "Could not verify credentials":
                return self.AccessTokenError
            if err.message == "Not connected":
                return self.ErrorDNS
            return self.OtherError
        return self.ErrorNotFound
