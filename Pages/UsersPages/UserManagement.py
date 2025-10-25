"""
UserManagement.py
=================

Module qui contient la classe UserManagement gérant la page qui gére les utilisateurs.

Dependencies:
    pyside6: Dépendance principale de l'application qui permet de créer des interfaces graphiques.
"""

# import des classes de Pyside6
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from Pages.UsersPages.SubPages.AddUserPage import AddUserPage
from Pages.UsersPages.SubPages.ViewUsersPage import ViewUserPage
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file


class UserManagement(QWidget):
    """Cette classe est la classe principale de la page gérant les utilisateurs.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): Classe client de l'API
        view_user_page (ViewUserPage): Classe de la page qui contient le tableau des utilisateurs.
    """

    def __init__(self, api: CrmApiAsync):
        """Constructeur de la classe UserManagement.

        Args:
            api (CrmApiAsync): Classe cliente de l'API.
        """
        super().__init__()
        self.api = api
        self.view_user_page = ViewUserPage(self.api)

        container = QWidget()

        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)
        layout_container.setContentsMargins(0, 0, 0, 0)

        container_tab_widget = QWidget()
        layout_tab_widget = QHBoxLayout(container_tab_widget)
        layout_tab_widget.setContentsMargins(0, 0, 0, 0)

        self.onglets = QTabWidget()
        self.onglets.setStyleSheet(load_qss_file("tab_bar.qss"))
        self.onglets.addTab(self.view_user_page, "UsersPages")
        self.onglets.addTab(AddUserPage(self.api, self.view_user_page), "Ajouter un utilisateur")
        layout_tab_widget.addWidget(self.onglets)
        layout_tab_widget.addWidget(container_tab_widget)
        layout_container.addWidget(container_tab_widget)

        container.setStyleSheet("""background: #0B1739""")

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
