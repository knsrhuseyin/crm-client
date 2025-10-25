"""
LoginPage.py
============

Module qui contient la classe de la page de connexion.

Dependencies:
    pyside6: Dépendance principale de l'application qui permet de créer des interfaces graphiques.
"""

# import de module
import asyncio

# import des classes de Pyside6
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QPushButton, QFormLayout, QCheckBox, \
    QSpacerItem, QFrame

from Pages.Panel import AdminPanel
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, update_json_file, center_on_screen


class LoginWindow(QWidget):
    """Classe de la page de connexion

    Attributes:
        api (CrmApiAsync): Classe client de l'API.
        email_input (QLineEdit): Le champ de l'email qui sera saisi par l'utilisateur.
        password_input (QLineEdit): Le champ du mot de passe qui sera saisie par l'utilisateur.
        info_label (QLabel): Le label qui informe l'état de la connexion.
        show_password_cb (QCheckBox): Checkbox permettant de voir le mot de passe.
        remember_cb (QCheckBox): Checkbox permettant d'enregistrer l'email et le mot de passe de l'utilisateur.
        login_btn (QPushButton): Bouton permettant la connexion.
    """

    def __init__(self, api: CrmApiAsync):
        """Constructeur de la page de connexion.

        Args:
            api (CrmApiAsync): Classe cliente de l'API.
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
        """
        Méthode d'initialisation de l'interface graphique de la page de connexion
        """
        self.setWindowTitle("Connexion")
        self.resize(1280, 720)
        center_on_screen(self)

        # Thème général bleu sombre
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
        card.setFixedWidth(400)
        card.setFixedHeight(600)
        card.setObjectName("card")
        card.setStyleSheet(load_qss_file("login_page.qss"))

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Titre
        title = QLabel("Connexion à votre compte")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #61dafb; padding: 15;")
        card_layout.addWidget(title)

        card_layout.addStretch()

        # Formulaire
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

        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        card_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout.addStretch()

        # Checkbox afficher le mot de passe
        self.show_password_cb = QCheckBox("Afficher le mot de passe")
        self.show_password_cb.setStyleSheet("color: #cdd6f4; font-size: 20px; padding: 5;")
        self.show_password_cb.stateChanged.connect(self.toggle_password)
        card_layout.addWidget(self.show_password_cb)

        # Checkbox se souvenir du mot de passe
        self.remember_cb = QCheckBox("Se souvenir du mot de passe")
        self.remember_cb.setStyleSheet("color: #cdd6f4; font-size: 20px; padding: 5; margin-bottom: 30px;")
        card_layout.addWidget(self.remember_cb)

        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(load_qss_file("button_style.qss"))
        self.login_btn.clicked.connect(lambda: asyncio.create_task(self.login()))
        card_layout.addWidget(self.login_btn)

        # Centrer la carte
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    # Afficher / masquer le mot de passe
    def toggle_password(self, state: int):
        """Méthode permettant d'afficher ou de masquer le mot de passe

        Args:
            state (int): Le status du champ.
        """
        if state == 2:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    # Progression...
    def set_progress(self, text: str, error: bool):
        """Méthode permettant de mettre à jour le label info_label

        Args:
            text (str): Texte du label info_label.
            error (bool): Si c'est une erreur ou pas.
        """
        if error:
            self.info_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            self.info_label.setText(text)
        else:
            self.info_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
            self.info_label.setText(text)

    # Connexion
    async def login(self):
        """
        Méthode principale permettant de connecter le client à l'API appelé après l'actionnement du bouton login_btn.
        """
        email = self.email_input.text()
        password = self.password_input.text()

        if email == "" or password == "":
            self.set_progress("Veuillez saisir vos identifiants !", False)
            return

        connexion = await self.api.login(email, password)
        self.set_progress("Chargement...", False)
        connexion_code = await self.api.verify_request(connexion)

        if connexion_code == self.api.Ok:
            self.info_label.setText("Connexion réussi !")
            if self.remember_cb.isChecked():
                update_json_file("auth.json", "email", email)
                update_json_file("auth.json", "password", password)
            self.admin_panel = AdminPanel(self.api)
            self.admin_panel.show()
            self.close()
        elif connexion_code == self.api.OtherError:
            if connexion["err"].message == "Wrong info !":
                self.set_progress("Les identifiants saisis sont incorrects !", True)
            else:
                self.set_progress("Une erreur a été rencontrée lors de la connexion !", True)
        elif connexion_code == self.api.ErrorNotFound:
            self.set_progress("Une erreur a été rencontrée lors de la connexion !", True)
