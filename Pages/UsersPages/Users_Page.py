from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from CRM_API import CrmApiAsync
from Pages.UsersPages.SubPages.AddUserPage import AddUserPage
from Pages.UsersPages.SubPages.ViewUsersPage import ViewUserPage
from utils.utils import load_qss_file


class UserManagement(QWidget):
    def __init__(self, api: CrmApiAsync):
        super().__init__()
        self.api = api
        self.users = []
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
