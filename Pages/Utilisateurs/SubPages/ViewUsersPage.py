import asyncio

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView

from CRM_API import CrmApiAsync


class ViewUserPage(QWidget):
    def __init__(self, api: CrmApiAsync, model):
        super().__init__()
        self.api = api
        self.model = model
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Les utilisateurs", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                    }
                """)
        layout.addWidget(title)

        asyncio.create_task(self.integer_users())

        self.user_table = QTreeView()
        self.model.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone"])

        self.user_table.setModel(self.model)
        self.user_table.setColumnWidth(3, 225)
        self.user_table.setSelectionMode(self.user_table.SelectionMode.SingleSelection)
        self.user_table.setEditTriggers(self.user_table.EditTrigger.NoEditTriggers)
        self.user_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.user_table.setDragEnabled(True)
        self.user_table.setDragDropMode(self.user_table.DragDropMode.NoDragDrop)
        self.user_table.setUniformRowHeights(True)
        self.user_table.setIndentation(0)
        self.user_table.setAllColumnsShowFocus(False)
        self.user_table.setSortingEnabled(True)
        self.user_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setRootIsDecorated(False)
        self.user_table.setStyleSheet("""
                    QHeaderView::section {
                        font-size: 17px;
                        background: #0D1B3A;
                        margin-left: 5px;                
                    }
                    QTreeView {
                        font-size: 15px;
                        gridline-color: white;
                    }
                    QTreeView::item {
                        padding: 5;
                        border: 1px solid rgba(255, 255, 255, 0.1);

                    }
                    QTreeView::item:focus {
                        outline: none;
                        border: 1px solid red;
                    }
                    QTreeView::item:hover {
                        background: rgba(255, 255, 255, 0.05)
                    }
                """)
        self.user_table.expandAll()

        layout.addWidget(self.user_table, 1)

        self.setLayout(layout)

    async def integer_users(self):
        users_data = await self.api.get_all_users()
        if "err" in users_data:
            users_data = await self.api.get_all_users()
        for user in users_data:
            print(user, "L.80, ViewUserPage.py")
            users = [
                QStandardItem(str(user["id"])),
                QStandardItem(user["name"]),
                QStandardItem(user["first_name"]),
                QStandardItem(user["email"]),
                QStandardItem(user["telephone"]),
            ]
            self.model.appendRow(users)
