"""
AddUserPage.py
==============

Ce module est le design de la page qui nous permet d'ajouter l'utilisateur.

Dependencies:
    pyside6: Dépendance principale afin de créer l'interface graphique ici pour créer la page AddUserPage.
"""

# import de module
import asyncio

# import des classes de Pyside6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QPushButton

from Pages.UsersPages.SubPages.ViewUsersPage import ViewUserPage
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, add_widgets


class AddUserPage(QWidget):
    """Le design de la page permettant d'ajouter un utilisateur.

    Attributes:
        api (CrmApiAsync): La classe de l'API permettant de faire des requêtes à la base de donnée.
        view_user_page (ViewUserPage): La page du tableau des utilisateurs qui va nous servir à émettre un signal apres
        l'ajout de l'utilisateur afin de mettre à jour le tableau.
        name (QLineEdit): Le champ pour mettre le nom du nouvel utilisateur.
        first_name (QLineEdit): Le champ pour mettre le prénom du nouvel utilisateur.
        email (QLineEdit): Le champ pour mettre l'email du nouvel utilisateur.
        telephone (QLineEdit): Le champ pour mettre le numéro de téléphone du nouvel utilisateur.
        info_label (QLabel): Un Label pour informer la progression de l'ajout.
        add_button (QPushButton): Le bouton permettant l'ajout de l'utilisateur.

    """

    def __init__(self, api: CrmApiAsync, view_user_page: ViewUserPage):
        """Constructeur de la page AddUserPage.

        Args:
            api (CrmApiAsync): la classe de l'API
            view_user_page (ViewUserPage): La page contenant le tableau des utilisateurs.
        """
        super().__init__()
        self.api = api
        self.view_user_page = view_user_page

        container = QWidget()

        layout = QVBoxLayout()
        container_layout = QVBoxLayout(container)
        title = QLabel("Ajouter un utilisateur", alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title.setStyleSheet("""padding: 0; font-size: 20px;""")
        container_layout.addWidget(title, 0)

        self.name = QLineEdit()
        self.first_name = QLineEdit()
        self.email = QLineEdit()
        self.telephone = QLineEdit()

        self.name.setPlaceholderText("Nom")
        self.first_name.setPlaceholderText("Prenom")
        self.email.setPlaceholderText("Email")
        self.telephone.setPlaceholderText("Telephone")

        self.info_label = QLabel()
        self.info_label.setStyleSheet("""font-size: 20px;""")

        self.add_button = QPushButton("Ajouter l'utilisateur")
        self.add_button.clicked.connect(lambda: asyncio.create_task(self.add_user_action()))
        self.add_button.setFixedWidth(300)
        self.add_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_widgets(container_layout,
                    [self.name, self.first_name, self.email, self.telephone, self.info_label])
        container_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignCenter)

        container.setStyleSheet(load_qss_file("add_user_page.qss"))

        container_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container, 1)
        layout.addStretch()

        self.setLayout(layout)

    # ------------------------------------------------------------
    #   Méthodes pour l'ajout de l'utilisateur
    # ------------------------------------------------------------

    async def set_progress(self, text: str, button_enabled: bool = True):
        """Méthode permettant de mettre à jour la progression de l'ajout de l'utilisateur.

        Args:
            text (str): Le texte qui sera indiqué au label.
            button_enabled (bool): Le status du bouton pour savoir si l'on peut appuyer ou non. Par défaut à False.
        """
        self.info_label.setText(text)
        self.add_button.setEnabled(button_enabled)

    async def add_user_action(self):
        """
        Méthode liée au bouton pour permettre l'ajout de l'utilisateur.
        """
        await self.set_progress("Chargement...", False)
        data = {
            "name": self.name.text(),
            "first_name": self.first_name.text(),
            "email": self.email.text(),
            "telephone": self.telephone.text()
        }

        if data["name"] == "" or data["first_name"] == "" or data["email"] == "" or data["telephone"] == "":
            await self.set_progress("Un des champs est vide !")
            return
        elif "@" not in data["email"]:
            await self.set_progress("L'email est incorrect !")
            return
        elif not data["telephone"].isdigit() or len(data["telephone"]) != 10:
            await self.set_progress("Le numéro de téléphone est incorrect !")
            return

        await self.set_progress("Chargement..", False)
        await self.add_user_to_database(data)

        self.add_button.setEnabled(True)

    async def add_user_to_database(self, data: dict):
        """Méthode permettant l'ajout de l'utilisateur dans la base de donnée externe via une requête à l'API.

        Args:
            data (dict): Les données de l'utilisateur qu'on veut ajouter.
        """
        response = await self.api.create_user(data["name"], data["first_name"], data["email"], data["telephone"])
        response_code = await self.api.verify_request(response)
        if response_code == self.api.Ok:
            self.view_user_page.refresh_users.emit()
            await self.set_progress("L'utilisateur a été ajouté avec succès !")
        elif response_code == self.api.UserReconnected:
            await self.add_user_to_database(data)
        elif response_code == self.api.AccessTokenError:
            await self.set_progress("Votre connexion a expiré ! Veuillez vous reconnecter !")
            return
        elif response_code == self.api.OtherError:
            if response["err"].message == 'User already exists!':
                print(response["err"].message)
                await self.set_progress("L'utilisateur existe déjà !")
                return
            elif response["err"].message == "Not authenticated":
                await self.set_progress("Vous n'êtes pas connecté !")
            else:
                print(response["err"].message)
                await self.set_progress("Un problème est survenu !")
                return
        elif response_code == self.api.ErrorNotFound:
            print(response)
            await self.set_progress("Un problème est survenu !")
            return
