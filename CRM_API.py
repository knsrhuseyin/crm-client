import asyncio
import json
import os.path
from json import JSONDecodeError
from typing import Optional, Dict, Any
from dotmap import DotMap

import aiohttp
from aiohttp import ClientResponseError

class CrmApiAsync:
    Ok: int = 200
    UserReconnected: int = 300
    AccessTokenError: int = 400
    OtherError: int = 450
    ErrorNotFound: int = 500

    """Client asynchrone générique pour gérer les requêtes HTTP"""
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.access_token_error = DotMap()
        self.access_token_error.err.message = "Could not verify creditials"

    async def _request(self, method: str, endpoint: str, progress_callback=None, **kwargs) -> Any:
        """Méthode interne qui gère toutes les requêtes HTTP"""
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
        """Envoie une requête GET"""
        return await self._request("GET", endpoint, params=params, headers=headers, progress_callback=progress_callback)

    async def post(self, endpoint: str, json: dict = None, data: Optional[Dict[str, Any]] = None, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête POST"""
        return await self._request("POST", endpoint, data=data, json=json, headers=headers, progress_callback=progress_callback)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête PUT"""
        return await self._request("PUT", endpoint, json=json, headers=headers, progress_callback=progress_callback)

    async def delete(self, endpoint: str, headers: dict = None, progress_callback=None) -> Any:
        """Envoie une requête DELETE"""
        return await self._request("DELETE", endpoint, headers=headers, progress_callback=progress_callback)

    async def login(self, username, password, progress_callback=None) -> bool:
        try:
            response = await self.post("auth/token", data={"username": username, "password": password}, progress_callback=progress_callback)
            print(response)
            self.headers = {"Authorization": f"Bearer {response["access_token"]}"}
            with open("token.json", "w") as f:
                json.dump({"access_token": response["access_token"]}, f)
            return True
        except ClientResponseError as e:
            print(e)
            return False

    async def create_user(self, name, first_name, email, telephone, progress_callback=None) -> dict:
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
        try:
            return await self.get(f"crm/users/{id}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_user_with_email(self, email: str, progress_callback=None) -> dict:
        try:
            return await self.get(f"crm/users/email/{email}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def update_user(self, user_id: int, modification: dict, progress_callback=None) -> dict:
        user = await self.get(f"crm/users/{user_id}", headers=self.headers)
        if "err" in user:
            print("Utilisateur introuvable")
            return {"err": user["err"]}
        new_data = {
            "name": user["name"] if "name" not in modification else modification["name"],
            "first_name": user["first_name"] if "first_name" not in modification else modification["first_name"],
            "email": user["email"] if "email" not in modification else modification["email"],
            "telephone": user["telephone"] if "telephone" not in modification else modification["telephone"]
        }
        try:
            return await self.put(f"crm/users/{user["id"]}", json=new_data, headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def delete_user(self, id, progress_callback=None) -> dict:
        try:
            return await self.delete(f"crm/users/{id}", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_all_users(self, progress_callback=None) -> dict:
        try:
            return await self.get("crm/users/", headers=self.headers, progress_callback=progress_callback)
        except ClientResponseError as e:
            return {"err": e}

    async def get_current_user_access(self, progress_callback=None) -> dict:
        if self.headers is not None:
            try:
                return await self.get("crm", headers=self.headers, progress_callback=progress_callback)
            except ClientResponseError as e:
                print(e)
                return {"err": e}
        else:
            if os.path.exists("token.json"):
                with open("token.json", "r") as f:
                    try:
                        token = json.load(f)["access_token"]
                    except JSONDecodeError as e:
                        print(e)
                if token is not None:
                    self.headers = {"Authorization": f"Bearer {token}"}
                    return await self.get_current_user_access()
                else:
                    os.remove("token.json")
                    return self.access_token_error
            else:
                return self.access_token_error




    async def verify_request(self, response: dict, auth_path: str) -> int:
        """
        Error code :
            200 -> Request OK
            300 -> User Reconnected
            400 -> Access Token Error
            450 -> Other Error
            500 -> Internal Server Error
        """
        if "err" not in response:
            return self.Ok
        else:
            if hasattr(response["err"], "message"):
                if response["err"].message == "Could not verify creditials":
                    if os.path.exists(auth_path):
                        with open(auth_path, "r") as f:
                            try:
                                login = json.load(f)
                            except JSONDecodeError as e:
                                print(e)
                        if login is not None:
                            if await self.login(**login):
                                return self.UserReconnected
                            else:
                                return self.AccessTokenError
                        else:
                            os.remove(auth_path)
                            return self.AccessTokenError
                    else:
                        return self.AccessTokenError
                else:
                    return self.OtherError
            else:
                print(response)
                return self.ErrorNotFound