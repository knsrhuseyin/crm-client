"""
AccountPage.py
==============

Module contenant la classe gérant la page d'accès au compte courant de l'utilisateur.

Dependencies:
    pyside6: Module principal du programme
"""
import asyncio
import os.path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QMessageBox

from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file


class AccountPage(QWidget):
    """Classe de la page de gestion de l'utilisateur courant.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): La classe cliente de l'API.
        parent (QWidget): Parent de la page de la page AccountPage.
        login_window (QWidget): La page de connexion pour rediriger après la déconnexion.
        name_label (QLabel): Label du nom de l'utilisateur courant.
        email_label (QLabel): Label de l'email de l'utilisateur courant.
        role_label (QLabel): Label du rôle de l'utilisateur courant.
        status_label (QLabel): Label du status de l'utilisateur courant.
        disconnect_btn (QPushButton): Le bouton de déconnexion.
    """
    def __init__(self, api: CrmApiAsync, parent: QWidget, login_window: QWidget):
        """Le constructeur de la page AccountPage.

        Args:
            api (CrmApiAsync): La classe cliente de l'API.
            parent (QWidget): Parent de la page AccountPage.
            login_window (QWidget): La page de connexion.
        """
        super().__init__()
        self.setWindowTitle("Informations du compte utilisateur")
        self.api = api
        self.parent = parent
        self.login_window = login_window
        self.name_label = None
        self.email_label = None
        self.role_label = None
        self.status_label = None
        self.disconnect_btn = None
        self.init_ui()

    def init_ui(self):
        """
        Constructeur de l'interface de AccountPage.
        """
        container = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        container_layout = QVBoxLayout(container)

        # Titre
        title = QLabel("Profil utilisateur courant")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px; padding: 10;")

        # Conteneur des infos
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                margin: 50px;
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: #1B263B;
                padding: 12;
            }
        """)

        frame_layout = QVBoxLayout()

        # Informations utilisateur
        self.name_label = QLabel()
        self.email_label = QLabel()
        self.role_label = QLabel()
        self.status_label = QLabel()

        asyncio.create_task(self.load_current_user_info())

        for label in [self.name_label, self.email_label, self.role_label, self.status_label]:
            label.setStyleSheet("font-size: 30px; margin: 3px; color: #E0E1DD;")

        # Bouton d'actualisation
        self.disconnect_btn = QPushButton("Se déconnecter")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.setStyleSheet(load_qss_file("button_style.qss"))
        self.disconnect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disconnect_btn.clicked.connect(self.disconnect_user_action)

        # Ajout au layout
        frame_layout.addWidget(self.name_label)
        frame_layout.addWidget(self.email_label)
        frame_layout.addWidget(self.role_label)
        frame_layout.addWidget(self.status_label)
        frame.setLayout(frame_layout)

        container_layout.addWidget(title)
        container_layout.addWidget(frame)
        container_layout.addStretch()
        container_layout.addWidget(self.disconnect_btn, alignment=Qt.AlignmentFlag.AlignRight)

        container.setStyleSheet("background-color: #0B1739;")

        container_layout.setContentsMargins(40, 40, 40, 40)
        layout.addWidget(container, 1)
        layout.addStretch()

        self.setLayout(layout)

    async def load_current_user_info(self):
        """
        Méthode permettant de récupérer les informations de l'utilisateur courant.
        """
        response = await self.api.get_current_user_access()
        response_code = await self.api.verify_request(response)

        if response_code == self.api.Ok:
            self.name_label.setText("Nom : " + response["current_user"]["name"])
            self.email_label.setText("Email : " + response["current_user"]["email"])
            self.role_label.setText("Rôle : " + response["current_user"]["role"])
            self.status_label.setText("Status : " + "Actif" if response["current_user"]["is_active"] else "Inactif")

    def disconnect_user_action(self):
        """
        Méthode permettant de déconnecter l'utilisateur courant et d'ouvrir la page de connexion.
        """
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if os.path.exists("auth.json"):
                os.remove("auth.json")
            self.login_window.show()
            self.parent.close()