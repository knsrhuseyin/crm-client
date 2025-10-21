import asyncio
import json
import os.path
from json import JSONDecodeError

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QPushButton
from aiohttp import ClientResponseError

from CRM_API import CrmApiAsync

class AddUserPage(QWidget):
    def __init__(self, api: CrmApiAsync, model: QStandardItemModel, admin_panel: QWidget):
        super().__init__()
        self.center_on_screen()
        self.api = api
        self.model = model
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

        self.add_button = QPushButton("Ajouter l'utilisateur")
        self.add_button.clicked.connect(lambda: asyncio.create_task(self.add_user_to_database()))
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

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    async def add_user_to_database(self):
        self.info_label.setText("Chargement.")
        data = {
            "name": self.name.text(),
            "first_name": self.first_name.text(),
            "email": self.email.text(),
            "telephone": self.telephone.text()
        }
        if data["name"] == "" or data["first_name"] == "" or data["email"] == "" or data["telephone"] == "":
            self.info_label.setText("Un des champs est vide !")
            return
        elif "@" not in data["email"]:
            self.info_label.setText("L'email est incorrect !")
            return
        elif not data["telephone"].isdigit() or len(data["telephone"]) != 10:
            self.info_label.setText("Le numéro de téléphone est incorrect !")
            return
        self.info_label.setText("Chargement..")
        self.info_label.setText("Chargement...")
        response = await self.api.create_user(data["name"], data["first_name"], data["email"], data["telephone"])
        if "err" in response:
            if hasattr(response["err"], "message"):
                if response["err"].message == 'User already exists!':
                    print(response["err"].message)
                    self.info_label.setText("L'utilisateur existe déjà !")
            elif response["err"] == "Access Token Error":
                if os.path.exists("auth.json"):
                    with open("auth.json", 'r') as f:
                        try:
                            login = json.load(f)
                        except JSONDecodeError as e:
                            print(e)
                            self.info_label.setText("Votre connexion a expiré, veuillez vous reconnecter !")
                            return
                    if await self.api.login(**login):
                        response = await self.api.create_user(data["name"], data["first_name"], data["email"],
                                                              data["telephone"])
                        if "err" in response:
                            if hasattr(response["err"], "message"):
                                if response["err"].message == 'User already exists!':
                                    print(response["err"].message)
                                    self.info_label.setText("L'utilisateur existe déjà !")
                        self.info_label.setText("L'utilisateur a été ajouté avec succès !")
                else:
                    self.info_label.setText("Votre connexion a expiré, veuillez vous reconnecter !")
            else:
                print(response["err"])
                print(type(response["err"]))
                self.info_label.setText("Un problème est survenu lors de l'ajout de l'utilisateur !")
        else:
            self.info_label.setText("Utilisateur ajouté avec succès !")
