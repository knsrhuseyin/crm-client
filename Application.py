"""
Application.py
==============

Module principale permettant de lancer l'application.
"""

import asyncio

import qasync
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar
from CRM_API import CrmApiAsync
from Pages.LoginPage import LoginWindow
from Pages.Panel import AdminPanel

class SplashScreen(QWidget):
    """Splash Screen permettant la connexion automatique de l'utilisateur.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): La casse de l'API.
        label (QLabel): La label pour informer du déroulement de la tâche.)
        progress_bar (QProgressBar): La progressbar pour indiquer le déroulement de la connexion.
    """
    def __init__(self, api: CrmApiAsync):
        """Fonction de l'initialisation du splash screen.

        Args:
            api (CrmApiAsync): La classe de l'API.
        """
        super().__init__()
        self.api = api
        self.setWindowTitle("Chargement...")
        self.resize(300, 150)
        self.center_on_screen()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222; color: white;")
        self.label = QLabel("🔄 Vérification de la session...", alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar()
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        # Lance la vérification sans bloquer
        QTimer.singleShot(0, lambda: asyncio.create_task(self.verify_session()))

    async def verify_session(self):
        """Fonction vérifie et connecte l'utilisateur courant.

        Cette fonction doit être appelée avec await.
        """
        async def fake_progress():
            for i in range(1, 91):
                await asyncio.sleep(0.02)
                self.progress_bar.setValue(i)

        fake_task = asyncio.create_task(fake_progress())

        connexion = await self.api.get_current_user_access(progress_callback=self.progress_bar.setValue)
        verify_connexion = await self.api.verify_request(connexion, "auth.json")

        fake_task.cancel()
        self.progress_bar.setValue(100)

        await asyncio.sleep(0.3)

        if verify_connexion == self.api.Ok:
            self.open_admin()
        elif verify_connexion == self.api.UserReconnected:
            await self.verify_session()
        elif verify_connexion == self.api.AccessTokenError:
            self.open_login()
        elif verify_connexion == self.api.OtherError:
            self.open_login()
        elif verify_connexion == self.api.ErrorNotFound:
            self.open_login()

    def center_on_screen(self):
        """
        Fonction permettant de centrer la page sur l'écran
        """
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def open_admin(self):
        """
        Fonction permettant d'ouvrir la page de l'administrateur pour la gestion des utilisateurs.
        """
        self.main = AdminPanel(self.api)
        self.main.show()
        self.close()

    def open_login(self):
        """
        Fonction permettant d'ouvrir la page de connexion.
        """
        self.login_page = LoginWindow(self.api)
        self.login_page.show()
        self.close()




async def main():
    """
    Fonction principale permettant l'ouverture de l'application en ouvrant le Splash Screen.
    """
    app = QApplication([])
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    api = CrmApiAsync("https://api-crm.knsr-family.com")

    splash = SplashScreen(api)
    splash.show()

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    """Lancement du programme"""
    asyncio.run(main())