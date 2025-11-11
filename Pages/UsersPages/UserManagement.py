"""
UserManagement.py
=================

Module contenant la page de gestion des utilisateurs du CRM.

Dependencies:
    PySide6: Pour la création de l'interface graphique.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from Pages.UsersPages.SubPages.AddUserPage import AddUserPage
from Pages.UsersPages.SubPages.ViewUsersPage import ViewUserPage
from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file


class UserManagement(QWidget):
    """Page principale pour la gestion des utilisateurs.

    Hérite de QWidget.

    Attributes:
        api (CrmApiAsync): Client API pour la communication avec le backend.
        view_user_page (ViewUserPage): Page affichant la liste des utilisateurs.
        onglets (QTabWidget): Onglets de navigation entre ajout et affichage des utilisateurs.
    """

    def __init__(self, api: CrmApiAsync):
        """Initialise la page de gestion des utilisateurs.

        Args:
            api (CrmApiAsync): Client API.
        """
        super().__init__()
        self.api = api
        self.view_user_page = ViewUserPage(self.api)
        self.onglets = None
        self.init_ui()

    def init_ui(self):
        """Construit l'interface graphique de la page UserManagement."""
        container = QWidget()
        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)
        layout_container.setContentsMargins(0, 0, 0, 0)

        container_tab_widget = QWidget()
        layout_tab_widget = QHBoxLayout(container_tab_widget)
        layout_tab_widget.setContentsMargins(0, 0, 0, 0)

        # Onglets
        self.onglets = QTabWidget()
        self.onglets.setStyleSheet(load_qss_file("tab_bar.qss"))
        self.onglets.addTab(self.view_user_page, "Liste des utilisateurs")
        self.onglets.addTab(AddUserPage(self.api, self.view_user_page), "Ajouter un utilisateur")

        layout_tab_widget.addWidget(self.onglets)
        layout_tab_widget.addWidget(container_tab_widget)  # Correction : inutile, mais conservé si besoin de future extension
        layout_container.addWidget(container_tab_widget)

        container.setStyleSheet("background: #0B1739;")
        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
