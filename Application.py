"""
Application.py
==============

Module principal permettant de lancer l'application.

Ce module initialise la boucle événementielle asynchrone,
configure l'interface graphique et lance l'écran de démarrage.

Dependencies:
    PySide6: Permet de créer des interfaces graphiques.
    qasync: Rend l'interface graphique compatible avec asyncio.
"""

# Imports standards
import asyncio

# Imports tiers
import qasync
from PySide6.QtWidgets import QApplication

# Imports internes
from Pages.SplashScreen import SplashScreen
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import get_icon


def main() -> None:
    """Lance l'application en affichant le Splash Screen.

    Cette fonction initialise l'application PySide6, configure la boucle
    événementielle asynchrone avec qasync, et démarre l'écran d'accueil
    avant de maintenir la boucle active.

    Example:
        >>> main()

    """
    app = QApplication([])
    app.setWindowIcon(get_icon("icon.ico"))
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    api = CrmApiAsync("https://api-crm.knsr-family.com", "auth.json")

    splash = SplashScreen(api)
    splash.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    # Point d'entrée du programme
    main()
