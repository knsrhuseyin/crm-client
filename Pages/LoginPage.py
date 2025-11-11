"""
LoginPage.py
============

Module contenant la page de connexion pour le CRM.

Dependencies:
    PySide6: Pour la création de l'interface graphique.
"""

import asyncio
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QPushButton,
    QFormLayout, QCheckBox, QSpacerItem, QFrame
)

from Pages.Panel import AdminPanel
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, update_json_file, center_on_screen


class LoginWindow(QWidget):
    """Page de connexion de l'application CRM.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): Client API pour la communication avec le backend.
        email_input (QLineEdit): Champ pour saisir l'email.
        password_input (QLineEdit): Champ pour saisir le mot de passe.
        info_label (QLabel): Label pour afficher l'état de la connexion.
        show_password_cb (QCheckBox): Checkbox pour afficher/masquer le mot de passe.
        remember_cb (QCheckBox): Checkbox pour mémoriser les identifiants.
        login_btn (QPushButton): Bouton pour lancer la connexion.
        admin_panel (AdminPanel | None): Fenêtre du panel administrateur après connexion réussie.
    """

    def __init__(self, api: CrmApiAsync):
        """Initialise la page de connexion.

        Args:
            api (CrmApiAsync): Client API.
        """
        super().__init__()
        self.api = api
        self.email_input = None
        self.password_input = None
        self.info_label = None
        self.show_password_cb = None
        self.remember_cb = None
        self.login_btn = None
        self.admin_panel = None
        self.init_ui()

    def init_ui(self):
        """Construit l'interface graphique de la page de connexion."""
        self.setWindowTitle("CRM Client")
        self.resize(1280, 720)
        center_on_screen(self)

        # Palette et thème
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0d1b2a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        self.setPalette(palette)
        self.setFont(QFont("Segoe UI", 10))

        # Layout principal centré
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Carte centrale
        card = QFrame()
        card.setFixedSize(400, 600)
        card.setObjectName("card")
        card.setStyleSheet(load_qss_file("login_page.qss"))

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Titre
        title = QLabel("Connexion à votre compte", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #61dafb; padding: 15;")
        card_layout.addWidget(title)
        card_layout.addStretch()

        # Formulaire email / mot de passe
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse e-mail")
        self.email_input.setStyleSheet(load_qss_file("input_style.qss"))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(load_qss_file("input_style.qss"))

        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        card_layout.addLayout(form_layout)

        # Label info
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        card_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addStretch()

        # Checkbox afficher le mot de passe
        self.show_password_cb = QCheckBox("Afficher le mot de passe")
        self.show_password_cb.setStyleSheet("color: #cdd6f4; font-size: 20px; padding: 5;")
        self.show_password_cb.stateChanged.connect(self.toggle_password)
        card_layout.addWidget(self.show_password_cb)

        # Checkbox se souvenir de l'utilisateur
        self.remember_cb = QCheckBox("Se souvenir de moi")
        self.remember_cb.setStyleSheet("color: #cdd6f4; font-size: 20px; padding: 5; margin-bottom: 30px;")
        card_layout.addWidget(self.remember_cb)

        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setStyleSheet(load_qss_file("button_style.qss"))
        self.login_btn.clicked.connect(lambda: asyncio.create_task(self.login()))
        card_layout.addWidget(self.login_btn)

        # Centrer la carte dans le layout principal
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    def toggle_password(self, state: int):
        """Affiche ou masque le mot de passe.

        Args:
            state (int): État de la checkbox.
        """
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if state == 2 else QLineEdit.EchoMode.Password
        )

    def set_progress(self, text: str, error: bool):
        """Met à jour le label d'information.

        Args:
            text (str): Message à afficher.
            error (bool): Si True, affiche le message en rouge.
        """
        color = "red" if error else "white"
        self.info_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        self.info_label.setText(text)

    async def login(self):
        """Tente de connecter l'utilisateur à l'API."""
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            self.set_progress("Veuillez saisir vos identifiants !", True)
            return

        connexion = await self.api.login(email, password)
        connexion_code = await self.api.verify_request(connexion)

        if connexion_code == self.api.Ok:
            self.set_progress("Connexion réussie !", False)
            if self.remember_cb.isChecked():
                update_json_file("auth.json", "access_token", connexion["access_token"])
            self.admin_panel = AdminPanel(self.api, LoginWindow(self.api))
            self.admin_panel.show()
            self.close()
        elif connexion_code == self.api.ErrorDNS:
            self.set_progress("Erreur de connexion\nVérifiez votre connexion internet !", True)
        elif connexion_code == self.api.OtherError:
            msg = getattr(connexion["err"], "message", "")
            if msg == "Wrong info!":
                self.set_progress("Les identifiants saisis sont incorrects !", True)
            else:
                self.set_progress("Une erreur a été rencontrée lors de la connexion !", True)
        elif connexion_code == self.api.ErrorNotFound:
            self.set_progress("Une erreur a été rencontrée lors de la connexion !", True)
