import asyncio
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QPushButton, QFormLayout, QCheckBox, \
    QSpacerItem, QFrame

from CODE_SOURCE_CRM.Application_Final.CRM_API import CrmApiAsync
from CODE_SOURCE_CRM.Application_Final.Pages.Panel import AdminPanel
from CODE_SOURCE_CRM.Database.database import DataBase


# login window CHATGPT
class LoginWindow(QWidget):
    def __init__(self, api: CrmApiAsync):
        super().__init__()
        self.api = api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Connexion")
        self.resize(1280, 720)

        # 🌌 Thème général bleu sombre
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0d1b2a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        self.setPalette(palette)

        self.setFont(QFont("Segoe UI", 10))

        # Layout principal centré
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🪶 Carte centrale
        card = QFrame()
        card.setFixedWidth(400)
        card.setFixedHeight(600)
        card.setStyleSheet("""
            QFrame {
                background-color: #1b263b;
                border-radius: 16px;
                border: 1px solid #23395d;
                box-shadow: 0px 0px 12px rgba(0, 0, 0, 80);
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # 🩵 Titre
        title = QLabel("Connexion à votre compte")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #61dafb; padding: 15;")
        card_layout.addWidget(title)

        card_layout.addStretch()

        # 📋 Formulaire
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse e-mail")
        self.email_input.setStyleSheet(self.input_style())

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.input_style())

        #form_layout.addRow("Email", )
        #form_layout.addRow("Mot de passe", self.password_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        card_layout.addLayout(form_layout)

        # 🔒 Checkbox afficher le mot de passe
        self.show_password_cb = QCheckBox("Afficher le mot de passe")
        self.show_password_cb.setStyleSheet("color: #cdd6f4; font-size: 20px;")
        self.show_password_cb.stateChanged.connect(self.toggle_password)
        card_layout.addWidget(self.show_password_cb)

        # 💾 Checkbox se souvenir du mot de passe
        self.remember_cb = QCheckBox("Se souvenir du mot de passe")
        self.remember_cb.setStyleSheet("color: #cdd6f4; font-size: 20px; padding: 10;")
        card_layout.addWidget(self.remember_cb)

        card_layout.addStretch()

        # 🚪 Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(self.button_style())
        self.login_btn.clicked.connect(lambda: asyncio.create_task(self.login()))
        card_layout.addWidget(self.login_btn)

        # Centrer la carte
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    # 🔐 Afficher / masquer le mot de passe
    def toggle_password(self, state):
        if state == 2:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    # 🎨 Style des champs de saisie
    def input_style(self):
        return """
            QLineEdit {
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                padding: 15;
                background-color: #16243d;
                color: white;
                margin-bottom: 10px;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #61dafb;
                background-color: #1b3350;
            }
        """

    # 🎨 Style du bouton
    def button_style(self):
        return """
            QPushButton {
                background-color: #144272;
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 20;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #205295;
            }
            QPushButton:pressed {
                background-color: #2C74B3;
            }
        """

    async def login(self):
        username = self.email_input.text()
        password = self.password_input.text()
        print(username, password)
        if await self.api.login(username, password):
            if self.remember_cb.isChecked():
                login_data = {
                    "username": username,
                    "password": password
                }
                with open("auth.json", "w") as f:
                    json.dump(login_data, f)
            self.admin_panel = AdminPanel(self.api)
            self.admin_panel.show()
            self.close()
        else:
            print("erreur")