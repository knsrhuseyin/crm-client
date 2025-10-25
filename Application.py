"""
Application.py
==============

Module principal permettant de lancer l'application.

Dependencies:
    pyside6: Dépendance principale de l'application qui permet de créer des interfaces graphiques.
    qasync: Dépendance permettant de rendre les interfaces graphiques asynchrones.
"""

# import de module.
import asyncio
import qasync

# import de classe Pyside6.
from PySide6.QtWidgets import QApplication

# import interne au programme.
from utils.CrmApiAsync import CrmApiAsync
from Pages.SplashScreen import SplashScreen


async def main():
    """
    Fonction principale permettant l'ouverture de l'application en ouvrant le Splash Screen.
    """
    app = QApplication([])
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    api = CrmApiAsync(URL, "auth.json")

    splash = SplashScreen(api)
    splash.show()

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    """Lancement du programme"""
    asyncio.run(main())
