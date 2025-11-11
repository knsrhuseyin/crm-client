"""
SplashScreen.py
===============

Module de la page SplashScreen permettant la connexion automatique de l'utilisateur.

Dependencies:
    PySide6: Pour la création de l'interface graphique.
    asyncio: Pour l'exécution asynchrone.
"""

import asyncio
from typing import Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout, QPushButton

from Pages.LoginPage import LoginWindow
from Pages.Panel import AdminPanel
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import center_on_screen, DraggableLabel


class SplashScreen(QWidget):
    """Splash Screen pour la connexion automatique de l'utilisateur.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): Client API pour interagir avec le backend.
        login_page (Optional[LoginWindow]): Page de connexion si l'utilisateur n'est pas connecté.
        admin_panel (Optional[AdminPanel]): Page administrateur si l'utilisateur est connecté.
        label (QLabel): Label affichant le déroulement de la connexion.
        progress_bar (QProgressBar): Barre de progression pour le feedback visuel.
        button_close (QPushButton): Bouton pour fermer le SplashScreen en cas d'erreur.
        button_reload (QPushButton): Bouton pour réessayer la connexion en cas d'erreur.
        author_label (DraggableLabel): Label affichant le créateur et la version du programme.
    """

    def __init__(self, api: CrmApiAsync):
        """Initialise le SplashScreen avec le client API.

        Args:
            api (CrmApiAsync): Instance du client API.
        """
        super().__init__()
        self.api = api
        self.login_page: Optional[LoginWindow] = None
        self.admin_panel: Optional[AdminPanel] = None
        self.label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.button_close: Optional[QPushButton] = None
        self.button_reload: Optional[QPushButton] = None
        self.author_label: Optional[DraggableLabel] = None
        self.init_ui()

    def init_ui(self):
        """Construit l'interface graphique du SplashScreen."""
        self.setWindowTitle("Splash CRM")
        self.resize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222; color: white;")
        center_on_screen(self)

        # Label auteur draggable
        self.author_label = DraggableLabel(
            "CRM Client | Created by knsrhuseyin | Version 1.1.0", self
        )
        self.author_label.setStyleSheet("font-size: 12px; color: gray;")
        self.author_label.setFixedHeight(30)

        # Label de message
        self.label = QLabel("Vérification de la session...", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Boutons
        self.button_close = QPushButton("Fermer")
        self.button_reload = QPushButton("Réessayer")
        self.button_reload.clicked.connect(lambda: asyncio.create_task(self.verify_session()))
        self.button_close.clicked.connect(self.close)
        self.button_reload.setVisible(False)
        self.button_close.setVisible(False)

        # Barre de progression
        self.progress_bar = QProgressBar()

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(2)
        layout.addWidget(self.author_label)
        layout.addWidget(self.label)
        layout.addWidget(self.button_reload)
        layout.addWidget(self.button_close)
        layout.addWidget(self.progress_bar)

        # Lance la vérification de session après l'initialisation
        QTimer.singleShot(0, lambda: asyncio.create_task(self.verify_session()))

    def message(self, text: str, err: bool = True):
        """Affiche un message et ajuste la visibilité des widgets.

        Args:
            text (str): Texte du message.
            err (bool): True si message d'erreur, False pour progression normale.
        """
        self.label.setText(text)
        self.progress_bar.setVisible(not err)
        self.button_close.setVisible(err)
        self.button_reload.setVisible(err)

    async def verify_session(self):
        """Vérifie et connecte l'utilisateur courant de manière asynchrone."""
        self.message("Vérification de la session...", False)

        # Simule une progression visuelle
        async def fake_progress():
            for i in range(1, 91):
                await asyncio.sleep(0.02)
                self.progress_bar.setValue(i)

        fake_task = asyncio.create_task(fake_progress())

        # Vérification réelle via l'API
        connexion = await self.api.get_current_user_access(progress_callback=self.progress_bar.setValue)
        verify_connexion = await self.api.verify_request(connexion)

        fake_task.cancel()
        self.progress_bar.setValue(100)
        await asyncio.sleep(0.3)

        # Gestion des résultats
        if verify_connexion == self.api.Ok:
            self.open_admin()
        elif verify_connexion == self.api.ErrorDNS:
            self.message("Erreur de connexion\nVeuillez vérifier votre connexion internet")
        else:
            self.open_login()

    # ------------------------------------------------------------
    # Méthodes pour ouvrir les pages correspondantes
    # ------------------------------------------------------------
    def open_admin(self):
        """Ouvre la page administrateur et ferme le SplashScreen."""
        self.admin_panel = AdminPanel(self.api, LoginWindow(self.api))
        self.admin_panel.show()
        self.close()

    def open_login(self):
        """Ouvre la page de connexion et ferme le SplashScreen."""
        self.login_page = LoginWindow(self.api)
        self.login_page.show()
        self.close()
