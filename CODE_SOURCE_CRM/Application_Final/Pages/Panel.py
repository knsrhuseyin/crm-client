from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QStackedWidget, QHBoxLayout, QListWidgetItem, \
    QListWidget

from CODE_SOURCE_CRM.Application_Final.CRM_API import CrmApiAsync
from CODE_SOURCE_CRM.Application_Final.Pages.Utilisateurs.Users_Page import UserManagement

class MenuWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.addItem(QListWidgetItem("Dashboard"))
        #self.addItem(QListWidgetItem("Test"))
        self.setCurrentRow(0)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("""
            QListWidget {
                margin: 10;
                border-radius: 2px;
                font-size: 20px;
            }
            QListWidget::item {
                padding: 15;

            }
            QListWidget::item:hover {
                background: #0A1330;
            }
            QListWidget::item:selected {
                background: #0A1330;
                border-left: 2px solid;
                border-color: #CB3CFF;
                font-weight: bold;
            }
        """)


class Panel(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.menu = MenuWidget()
        self.stacked_widget = stacked_widget

        self.menu.currentRowChanged.connect(self.change_page)


        container = QWidget()

        layout = QVBoxLayout()
        layout_container = QVBoxLayout(container)
        title = QLabel("Admin Panel", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                padding: 10;
                font-size: 20px;
                margin:10;
                font-weight: bold;
            }
        """)
        layout_container.addWidget(title)
        layout_container.addWidget(self.menu)

        layout_container.setContentsMargins(0, 0, 0, 0)
        layout_container.setSpacing(0)

        container.setStyleSheet("""background: #081028;""")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setMaximumWidth(300)
        self.setLayout(layout)

    def change_page(self, index):
        """Change la page affichée dans le QStackedWidget"""
        self.stacked_widget.setCurrentIndex(index)


class AdminPanel(QWidget):
    def __init__(self, api: CrmApiAsync):
        super().__init__()
        self.resize(1280, 720)

        self.pages = QStackedWidget()
        self.pages.addWidget(UserManagement(api, self))

        layout = QHBoxLayout()
        layout.addWidget(Panel(self.pages))
        layout.addWidget(self.pages)


        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)