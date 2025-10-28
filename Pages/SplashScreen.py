"""
SplashScreen.py
===============

Module de la page SplashScreen.

Dependencies:
    pyside6: Module principal du programme.
"""

# import de module
import asyncio

# import des classes de pyside6
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout

# import interne au programme
from Pages.LoginPage import LoginWindow
from Pages.Panel import AdminPanel
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import center_on_screen


class SplashScreen(QWidget):
    """Splash Screen permettant la connexion automatique de l'utilisateur.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): La classe cliente de l'API.
        login_page (LoginPage): La page de connexion si l'utilisateur n'est pas connecté.
        admin_panel (AdminPanel): La page administrateur si l'utilisateur est connecté.
        label (QLabel): Le label qui sert à informer le déroulement de la connexion.
        progress_bar (QProgressBar): La barre de progression pour indiquer le déroulement de la connexion.
    """

    def __init__(self, api: CrmApiAsync):
        """Constructeur de la classe SplashScreen.

        Args:
            api (CrmApiAsync): La classe de l'API.
        """
        super().__init__()
        self.api = api
        self.login_page = None
        self.admin_panel = None
        self.label = None
        self.progress_bar = None
        self.init_ui()

    def init_ui(self):
        """
        Constructeur de l'interface graphique de la page SplashScreen.
        """
        self.setWindowTitle("Chargement...")
        self.resize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222; color: white;")

        center_on_screen(self)

        self.label = QLabel("🔄 Vérification de la session...", alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar()

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        # Lance la vérification sans bloquer
        QTimer.singleShot(0, lambda: asyncio.create_task(self.verify_session()))

    async def verify_session(self):
        """Méthode qui vérifie et connecte l'utilisateur courant.

        Cette fonction doit être appelée avec await.
        """

        async def fake_progress():
            """Fonction mettant en oeuvre une fausse progression.

            Fonction interne de la méthode verify_session.
            """
            for i in range(1, 91):
                await asyncio.sleep(0.02)
                self.progress_bar.setValue(i)

        fake_task = asyncio.create_task(fake_progress())

        connexion = await self.api.get_current_user_access(progress_callback=self.progress_bar.setValue)
        verify_connexion = await self.api.verify_request(connexion)

        fake_task.cancel()
        self.progress_bar.setValue(100)

        await asyncio.sleep(0.3)

        # Vérification de la requête.
        if verify_connexion == self.api.Ok:
            self.open_admin()
        elif verify_connexion == self.api.AccessTokenError:
            self.open_login()
        elif verify_connexion == self.api.OtherError:
            self.open_login()
        elif verify_connexion == self.api.ErrorNotFound:
            self.open_login()

    # ------------------------------------------------------------
    #   Les fonctions permettant de charger la page concernée
    # ------------------------------------------------------------
    def open_admin(self):
        """
        Méthode permettant d'ouvrir la page de l'administrateur pour la gestion des utilisateurs.
        """
        self.admin_panel = AdminPanel(self.api, LoginWindow(self.api))
        self.admin_panel.show()
        self.close()

    def open_login(self):
        """
        Méthode permettant d'ouvrir la page de connexion.
        """
        self.login_page = LoginWindow(self.api)
        self.login_page.show()
        self.close()
