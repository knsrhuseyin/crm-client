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


class AccountPage(QWidget):
    """Classe de la page de gestion de l'utilisateur courant

    """
    def __init__(self, api: CrmApiAsync, parent, login_window):
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
        self.disconnect_btn = QPushButton("Se deconnecter")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E6091;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 30px 60px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #184E77;
            }
        """)
        self.disconnect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disconnect_btn.clicked.connect(self.disconnect)

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
        response = await self.api.get_current_user_access()
        response_code = await self.api.verify_request(response)

        if response_code == self.api.Ok:
            self.name_label.setText("Nom : " + response["current_user"]["name"])
            self.email_label.setText("Email : " + response["current_user"]["email"])
            self.role_label.setText("Rôle : " + response["current_user"]["role"])
            self.status_label.setText("Status : " + "Actif" if response["current_user"]["is_active"] else "Inactif")

    def disconnect(self):
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