from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from CODE_SOURCE_CRM.Application_Final.CRM_API import CrmApiAsync
from CODE_SOURCE_CRM.Application_Final.Pages.Utilisateurs.SubPages.AddUserPage import AddUserPage
from CODE_SOURCE_CRM.Application_Final.Pages.Utilisateurs.SubPages.ViewUsersPage import ViewUserPage


class UserManagement(QWidget):
    def __init__(self, api: CrmApiAsync, admin_panel: QWidget):
        super().__init__()
        self.api = api
        self.users = []
        self.model = QStandardItemModel()
        self.admin_panel = admin_panel

        container = QWidget()

        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)
        layout_container.setContentsMargins(0, 0, 0, 0)

        container_tab_widget = QWidget()
        layout_tab_widget = QHBoxLayout(container_tab_widget)
        layout_tab_widget.setContentsMargins(0, 0, 0, 0)

        self.onglets = QTabWidget()
        self.onglets.addTab(ViewUserPage(self.api, self.model), "Utilisateurs")
        self.onglets.addTab(AddUserPage(self.api, self.model, self.admin_panel), "Ajouter un utilisateur")
        self.onglets.setStyleSheet("""
            QTabBar {
                border-top: 10px;
            }
            QTabBar::tab {
                background: #0A1330;
                margin-top: 10px;
                width: 110px;
                padding: 10px;
                border-color: #0B1739;
                border-radius: 2px;
            }
            QTabBar::tab:hover {
                background: #081028;
            }
            QTabBar::tab:selected {
                background: #081028;
            }
        """)
        layout_tab_widget.addWidget(self.onglets)
        layout_tab_widget.addWidget(container_tab_widget)
        layout_container.addWidget(container_tab_widget)

        container.setStyleSheet("""background: #0B1739""")

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
