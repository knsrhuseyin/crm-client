import asyncio
import json
import os.path
import sys
from json import JSONDecodeError

import qasync
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QStackedWidget, QWidget, QLabel, QVBoxLayout
from aiohttp import ClientResponseError

from CODE_SOURCE_CRM.Application_Final.CRM_API import CrmApi, CrmApiAsync
from CODE_SOURCE_CRM.Application_Final.Pages.LoginPage import LoginWindow
from CODE_SOURCE_CRM.Application_Final.Pages.Panel import AdminPanel
from CODE_SOURCE_CRM.Database.database import DataBase

class SplashScreen(QWidget):
    def __init__(self, api: CrmApiAsync):
        super().__init__()
        self.api = api
        self.setWindowTitle("Chargement...")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222; color: white;")
        self.label = QLabel("🔄 Vérification de la session...", alignment=Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        # Lance la vérification sans bloquer
        QTimer.singleShot(0, lambda: asyncio.create_task(self.verify_session()))

    async def verify_session(self):
        is_authenticated = await self.api.get_current_user_access()
        await asyncio.sleep(0.5)  # pour garder l’effet visuel du splash

        if is_authenticated:
            self.open_admin()
            print("ici")
        elif os.path.exists("auth.json"):
            with open("auth.json", 'r') as f:
                try:
                    login = json.load(f)
                except JSONDecodeError as e:
                    print(e)
                    self.open_login()
            if await self.api.login(login["username"], login["password"]):
                self.open_admin()
            else:
                print("Les informations de connexions sont fausses.")
                os.remove("auth.json")
        else:
            self.open_login()

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