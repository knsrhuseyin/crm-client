"""
CrmApiAsync.py
==============

Module de la classe cliente à l'API gérant les requêtes.

Dependencies:
    json: manipulations des fichiers json
    dotmap: Pour ajouter des attributs dans les dictionnaires
    aiohttp: Pour l'exception rencontrée lors de la requête effectuée grâce àa la class Requests.
"""
# import module
import os.path
# import module python
from typing import Optional, Dict

# import de classe des modules externes
from aiohttp import ClientResponseError
from dotmap import DotMap

# import interne au programme
from utils.Requests import Requests
from utils.utils import update_json_file, get_data_json, get_key_data_json


class CrmApiAsync(Requests):
    """Cette classe gére le côté client de l'API faisant des requêtes à la base de donnée.

    Hérite de Requests.

    Attributes:
        Ok (int): Code 200 signifiant que la requête a bien été réussi.
        UserReconnected (int): Code 300 signifiant que l'utilisateur a été reconnecté suite à une expiration de clé.
        AccessTokenError (int): Code 400 signifiant que le token est expiré et que l'utilisateur n'a pas pu être reconnecté.
        OtherError (int): Code 450 signifiant qu'une erreur a été retrouvé lors de la requête.
        ErrorNotFound (int): Code 500 signifiant qu'une erreur externe a été retrouvé lors de la requête.
        auth_file (str): Attribut stockant la destination du fichier stockant les informations d'authentifications.
    """
    Ok: int = 200
    UserReconnected: int = 300
    AccessTokenError: int = 400
    OtherError: int = 450
    ErrorNotFound: int = 500

    def __init__(self, base_url: str, auth_file: str, headers: Optional[Dict[str, str]] = None):
        """Constructeur de la classe CrmApiAsync héritant de Requests.

        Args:
            base_url (str): L'url de l'API.
            headers (Optional[Dict[str, str]]): La clé qui est définie généralement dans la classe CrmApiAsync.
            auth_file (str): Destination du fichier stockant les informations d'authentifications.
        """
        super().__init__(base_url, headers)
        self.auth_file = auth_file

    async def login(self, email, password, progress_callback=None) -> dict:
        """La méthode qui nous permet de nous connecter à l'API.

        Cette fonction doit être appelée avec await.

        Args:
            email (str): l'email de l'utilisateur client.
            password (str): le mot de passe de l'utilisateur client.
            progress_callback (Optional[None]]): Paramètre permettant de donner la progression de la requête.
        """
        try:
            response = await self.post("auth/token", data={"username": email, "password": password},
                                       progress_callback=progress_callback)
            self.headers = {"Authorization": f"Bearer {response["access_token"]}"}
            update_json_file(self.auth_file, "access_token", response["access_token"])
            return response
        except ClientResponseError as e:
            return {"err": e}

    async def create_user(self, name, first_name, email, telephone, progress_callback=None) -> dict:
        """Méthode permettant d'ajouter un utilisateur à la base de donnée.

        Cette fonction doit être appelée avec await.

        Args:
            name (str): Nom d nouvel l'utilisateur.
            first_name (str): Prénom du nouvel utilisateur.
            email (str): Email du nouvel utilisateur.
            telephone (str): Telephone du nouvel utilisateur.
            progress_callback (Optional[None]): Paramètre permettant de donner la progression de la requête.

        Returns:
            dict: les données de l'utilisateur ajouté s'il est ajouté avec succès sinon l'erreur rencontrée.
        """
        data = {
            "name": name,
            "first_name": first_name,
            "email": email,
            "telephone": telephone
        }
        try:
            return await self.post("crm/users/", json=data, headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_user(self, id, progress_callback=None) -> dict:
        """Méthode permettant de récupérer un utilisateur de la base de donnée via son ID.

        Cette fonction doit être appelée avec await.

        Args:
            id (int): ID de l'utilisateur qu'on veut récupérer.
            progress_callback (Optional[None]): Paramètre permettant de donner la progression de la requête.

        Returns:
            dict: Les données de l'utilisateur sinon l'erreur rencontrée.
        """
        try:
            return await self.get(f"crm/users/{id}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_user_with_email(self, email: str, progress_callback=None) -> dict:
        """Méthode permettant de récupérer un utilisateur de la base de donnée via son email.

        Cette fonction doit être appelée avec await.

        Args:
            email (int): Email de l'utilisateur qu'on veut récupérer.
            progress_callback (Optional[None]): Fonction permettant de donner la progression de la requête.

        Returns:
            dict: Les données de l'utilisateur sinon l'erreur rencontrée.
        """
        try:
            return await self.get(f"crm/users/email/{email}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def update_user(self, user_id: int, modification: dict, progress_callback=None) -> dict:
        """Méthode permettant de mettre à jour un utilisateur de la base de donnée via son ID.

        Cette fonction doit être appelée avec await.

        Args:
            user_id (int): ID de l'utilisateur qu'on veut mettre à jour.
            modification (dict): les nouvelles données de l'utilisateur qu'on veut modifier.
            progress_callback (Optional[None]): Fonction permettant de donner la progression de la requête.

        Returns:
            dict: Les nouvelles données de l'utilisateur qu'on a modifié sinon l'erreur rencontrée.
        """
        new_data = {
            "name": modification["name"],
            "first_name": modification["first_name"],
            "email": modification["email"],
            "telephone": modification["telephone"]
        }
        try:
            return await self.put(f"crm/users/{user_id}", json=new_data, headers=self.headers,
                                  progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def delete_user(self, id, progress_callback=None) -> dict:
        """Méthode permettant de supprimer un utilisateur de la base de donnée via son ID.

        Cette fonction doit être appelée avec await.

        Args:
            id (int): ID de l'utilisateur qu'on veut supprimer.
            progress_callback (Optional[None]): Fonction permettant de donner la progression de la requête.

        Returns:
            dict: Confirme la suppression de l'utilisateur sinon renvoie une erreur.
        """
        try:
            return await self.delete(f"crm/users/{id}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_all_users(self, progress_callback=None) -> dict:
        """Méthode permettant de récupérer tous les utilisateurs de la base de donnée.

        Cette fonction doit être appelée avec await.

        Args:
            progress_callback (Optional[None]): Fonction permettant de donner la progression de la requête.

        Returns:
            dict: Les données des utilisateurs sinon l'erreur rencontrée.
        """
        try:
            return await self.get("crm/users/", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_current_user_access(self, progress_callback=None) -> dict:
        """Méthode vérifiant si l'utilisateur courant est récupérable ou non.

        Cette fonction doit être appelée avec await.

        Args:
            progress_callback (Optional[None]): Fonction permettant de donner la progression de la requête.

        Returns:
            dict: Renvoie l'utilisateur courant sinon l'erreur rencontrée.
        """
        access_token_error = DotMap()
        access_token_error.err.message = "Could not verify creditials"
        if self.headers is not None:
            try:
                return await self.get("crm", headers=self.headers, progress_callback=progress_callback)
            except ClientResponseError as e:
                print(e)
                return {"err": e}
        else:
            token = get_key_data_json(self.auth_file, "access_token")
            if token is not None:
                self.headers = {"Authorization": f"Bearer {token}"}
                return await self.get_current_user_access()
            else:
                if os.path.exists(self.auth_file):
                    os.remove("../auth.json")
                return access_token_error

    async def verify_request(self, response: dict) -> int:
        """Méthode vérifiant l'état de la requête associée.

        Cette fonction doit être appelée avec await.

        Args:
            response (dict): La requête effectuée.

        Returns:
            int: Le code concernant l'état de la requête via les attributs définis plus tôt dans la classe.
        """
        if "err" not in response:
            return self.Ok
        else:
            if hasattr(response["err"], "message"):
                if response["err"].message == "Could not verify creditials":
                    auth_file = get_data_json(self.auth_file)
                    if auth_file is not None and "email" in auth_file and "password" in auth_file:
                        if await self.login(auth_file["email"], auth_file["password"]):
                            return self.UserReconnected
                        else:
                            os.remove(self.auth_file)
                            return self.AccessTokenError
                    else:
                        if os.path.exists(self.auth_file):
                            os.remove(self.auth_file)
                        return self.AccessTokenError
                else:
                    return self.OtherError
            else:
                return self.ErrorNotFound
