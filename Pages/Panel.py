"""
Panel.py
========

Ce module contient la géstion et le design du panel administrateur.

Dependencies:
    pyside6: Module principal du programme.
"""

# import des classes de pyside6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QStackedWidget, QHBoxLayout, QListWidgetItem, \
    QListWidget

from Pages.AccountPage.AccountPage import AccountPage
from Pages.UsersPages.UserManagement import UserManagement
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, center_on_screen


class MenuWidget(QListWidget):
    """Cette classe permet d'ajouter les éléments qui seront contenus dans le menu de l'admin panel.

    Hérite de QListWidget
    """

    def __init__(self):
        """
        Constructeur du menu de l'admin panel
        """
        super().__init__()
        self.setFixedWidth(300)
        self.addItem(QListWidgetItem("Gestion des utilisateurs"))
        self.addItem(QListWidgetItem("Mon compte"))
        self.setCurrentRow(0)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(load_qss_file("menu_widget.qss"))


class Panel(QWidget):
    """Classe gérant le changement de page du Panel.

    Hérite de QWidget.

    Attributes:
        menu (MenuWidget): La classe MenuWidget qu'on a créé ultérieurement.
        stacked_widget (QStackedWidget): La classe qui contient les pages accessible via le panel et nous permet de changer la page.
    """

    def __init__(self, stacked_widget: QStackedWidget):
        """Constructeur du panel.

        Args:
            stacked_widget (QStackedWidget): classe qui contient les pages accessible via le panel
        """
        super().__init__()

        self.menu = MenuWidget()
        self.stacked_widget = stacked_widget

        self.menu.currentRowChanged.connect(self.change_page)

        container = QWidget()

        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)

        title = QLabel("Admin Panel", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""padding: 10; font-size: 20px; margin:10; font-weight: bold;""")

        creator = QLabel("Created by knsrhuseyin", alignment=Qt.AlignmentFlag.AlignCenter)
        creator.setStyleSheet("""padding: 5; font-size: 15px; margin-bottom:5; color: gray;""")

        layout_container.addWidget(title)
        layout_container.addWidget(self.menu)
        layout_container.addWidget(creator)

        layout_container.setContentsMargins(0, 0, 0, 0)
        layout_container.setSpacing(0)

        container.setStyleSheet("""background: #081028;""")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setMaximumWidth(300)
        self.setLayout(layout)

    def change_page(self, index: int):
        """Méthode permettant de changer la page affichée dans le QStackedWidget.

        Args:
            index (int): Chiffre permettant d'indiquer la page à afficher.
        """
        self.stacked_widget.setCurrentIndex(index)


class AdminPanel(QWidget):
    """Classe de la page du Panel.

    Hérite de QWidget.

    Attributes:
        pages (QStackedWidget): Les pages qui seront accessible via le panel sont ajoutés ici.
    """

    def __init__(self, api: CrmApiAsync, login_window):
        """Constructeur de l'affichage de l'AdminPanel.

        Args:
            api (CrmApiAsync): Classe cliente de l'API.
        """
        super().__init__()
        self.resize(1280, 720)
        center_on_screen(self)

        self.pages = QStackedWidget()
        self.pages.addWidget(UserManagement(api))
        self.pages.addWidget(AccountPage(api, self, login_window))

        layout = QHBoxLayout()
        layout.addWidget(Panel(self.pages))
        layout.addWidget(self.pages)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
