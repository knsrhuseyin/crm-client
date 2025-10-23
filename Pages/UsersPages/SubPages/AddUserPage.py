import asyncio
import json
import os.path
from json import JSONDecodeError

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QGuiApplication, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QPushButton, QProgressBar
from aiohttp import ClientResponseError

from CRM_API import CrmApiAsync
from Pages.UsersPages.SubPages.ViewUsersPage import ViewUserPage


class AddUserPage(QWidget):
    def __init__(self, api: CrmApiAsync, view_user_page: ViewUserPage, admin_panel: QWidget):
        super().__init__()
        self.api = api
        self.view_user_page = view_user_page
        self.admin_panel = admin_panel

        container = QWidget()

        layout = QVBoxLayout()
        container_layout = QVBoxLayout(container)
        title = QLabel("Ajouter un utilisateur", alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title.setStyleSheet("""
            QLabel {
                padding: 0;
                font-size: 20px;
            }
        """)
        container_layout.addWidget(title, 0)

        self.name = QLineEdit()
        self.first_name = QLineEdit()
        self.email = QLineEdit()
        self.telephone = QLineEdit()

        container_layout.addWidget(self.name)
        container_layout.addWidget(self.first_name)
        container_layout.addWidget(self.email)
        container_layout.addWidget(self.telephone)

        self.name.setPlaceholderText("Nom")
        self.first_name.setPlaceholderText("Prenom")
        self.email.setPlaceholderText("Email")
        self.telephone.setPlaceholderText("Telephone")

        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
            }
        """)
        container_layout.addWidget(self.info_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
            }
        """)
        container_layout.addWidget(self.progress_bar)

        self.add_button = QPushButton("Ajouter l'utilisateur")
        self.add_button.clicked.connect(lambda: asyncio.create_task(self.add_user_action()))
        self.add_button.setFixedWidth(300)
        self.add_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        container_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignCenter)

        container.setStyleSheet("""
            QLineEdit {
                margin-top: 10px;
                font-size: 20px;
                padding: 10;
                border: 3px solid #13254D;
                border-radius: 2px;
            }
            QLineEdit:hover {
                border: 2px solid #61dafb;
                background-color: #1b3350;
            }
            QLineEdit:focus {
                border: 2px solid #61dafb;
                background-color: #1b3350;
            }
            QPushButton {
                padding: 20;
                font-size: 20px;
            }
            QPushButton:hover {
                 background: #13254D;
            }
        """)

        container_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container, 1)
        layout.addStretch()


        self.setLayout(layout)

    # ------------------------------
    #
    # ------------------------------

    async def set_progress(self, text: str, button_enabled: bool = True, progress: int = 0):
        """Mets à jour la progression de l'ajout de l'utilisateur.

        Args:
            text (str): Le texte qui sera indiqué au label.
            button_enabled (bool): Le status du bouton pour savoir si l'on peut appuyer ou non. Par défaut à False.
            progress (int): Le status de la progression pour mettre à jour la progress bar. Par défaut à 0.

        """
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(True)
        if button_enabled:
            await asyncio.sleep(0.1)
            self.progress_bar.setVisible(False)
        self.info_label.setText(text)
        self.add_button.setEnabled(button_enabled)
        if self.progress_bar.value() == 0:
            await asyncio.sleep(0.1)
            self.progress_bar.setVisible(False)

    async def add_user_action(self):
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

        await self.set_progress("Chargement..", False, 50)
        await self.add_user_to_database(data)

        self.add_button.setEnabled(True)

    async def add_user_to_database(self, data):
        response = await self.api.create_user(data["name"], data["first_name"], data["email"], data["telephone"],
                                              progress_callback=self.progress_bar.setValue)
        response_code = await self.api.verify_request(response, "auth.json")
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
            else:
                print(response["err"].message)
                await self.set_progress("Un problème est survenu !")
                return
        elif response_code == self.api.ErrorNotFound:
            print(response)
            await self.set_progress("Un problème est survenu !")
            return