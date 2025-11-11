"""
Panel.py
========

Module gérant le panel administrateur et le menu de navigation.

Dependencies:
    PySide6: Module principal pour l'interface graphique.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QHBoxLayout,
    QListWidgetItem,
    QListWidget,
)

from Pages.AccountPage.AccountPage import AccountPage
from Pages.UsersPages.UserManagement import UserManagement
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, center_on_screen, get_icon


class MenuWidget(QListWidget):
    """Menu latéral du panel administrateur.

    Hérite de QListWidget et contient les items du menu.
    """

    def __init__(self):
        """Initialise le menu avec les éléments prédéfinis."""
        super().__init__()
        self.setFixedWidth(300)
        self.addItem(QListWidgetItem("Gestion des utilisateurs"))
        self.addItem(QListWidgetItem("Mon compte"))
        self.setCurrentRow(0)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(load_qss_file("menu_widget.qss"))


class Panel(QWidget):
    """Widget du panel contenant le menu et gérant le changement de page.

    Attributes:
        menu (MenuWidget): Menu de navigation.
        stacked_widget (QStackedWidget): Conteneur des pages accessibles via le panel.
    """

    def __init__(self, stacked_widget: QStackedWidget):
        """Initialise le panel avec le menu et la structure graphique.

        Args:
            stacked_widget (QStackedWidget): Conteneur des pages.
        """
        super().__init__()

        self.menu = MenuWidget()
        self.stacked_widget = stacked_widget
        self.menu.currentRowChanged.connect(self.change_page)

        container = QWidget()
        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)

        # Section icône et titre
        icon_widget = QWidget()
        icon_layout = QHBoxLayout(icon_widget)

        title_icon = QLabel()
        title_icon.setPixmap(get_icon("icon.ico", True).scaled(48, 48))
        title_icon.setStyleSheet("padding: 10px; font-size: 20px; margin: 10px; font-weight: bold;")

        title = QLabel("AdminPanel")
        title.setStyleSheet("font-size: 24px;")

        icon_layout.addWidget(title_icon)
        icon_layout.addWidget(title)
        icon_layout.addStretch()

        # Footer créateur/version
        creator = QLabel("Created by knsrhuseyin | Version 1.1.0", alignment=Qt.AlignmentFlag.AlignCenter)
        creator.setStyleSheet("padding: 5px; font-size: 15px; margin-bottom:5px; color: gray;")

        # Assemblage layout
        layout_container.addWidget(icon_widget)
        layout_container.addWidget(self.menu)
        layout_container.addWidget(creator)

        layout_container.setContentsMargins(0, 0, 0, 0)
        layout_container.setSpacing(0)

        container.setStyleSheet("background: #081028;")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setMaximumWidth(300)
        self.setLayout(layout)

    def change_page(self, index: int):
        """Change la page affichée dans le QStackedWidget.

        Args:
            index (int): Index de la page à afficher.
        """
        self.stacked_widget.setCurrentIndex(index)


class AdminPanel(QWidget):
    """Fenêtre principale du panel administrateur.

    Contient le menu et les pages accessibles via le panel.
    """

    def __init__(self, api: CrmApiAsync, login_window):
        """Initialise la fenêtre AdminPanel.

        Args:
            api (CrmApiAsync): Client API pour la communication avec le backend.
            login_window (QWidget): Fenêtre de login, pour référence dans AccountPage.
        """
        super().__init__()
        self.resize(1280, 720)
        self.setWindowTitle("CRM Client")
        center_on_screen(self)

        # Création des pages accessibles
        self.pages = QStackedWidget()
        self.pages.addWidget(UserManagement(api))
        self.pages.addWidget(AccountPage(api, self, login_window))

        # Layout principal
        layout = QHBoxLayout()
        layout.addWidget(Panel(self.pages))
        layout.addWidget(self.pages)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
