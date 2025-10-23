import asyncio
import json
import os.path
from json import JSONDecodeError

import qasync
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar
from CRM_API import CrmApiAsync
from Pages.LoginPage import LoginWindow
from Pages.Panel import AdminPanel

class SplashScreen(QWidget):
    def __init__(self, api: CrmApiAsync):
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
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def open_admin(self):
        self.main = AdminPanel(self.api)
        self.main.show()
        self.close()

    def open_login(self):
        self.login_page = LoginWindow(self.api)
        self.login_page.show()
        self.close()




async def main():
    app = QApplication([])
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    api = CrmApiAsync("https://api-crm.knsr-family.com")

    splash = SplashScreen(api)
    splash.show()

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())