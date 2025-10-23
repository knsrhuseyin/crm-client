import asyncio

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QGuiApplication, QStandardItemModel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QPushButton, QMessageBox, QHBoxLayout, QLineEdit

from CRM_API import CrmApiAsync
from utils.utils import load_qss_file


class ViewUserPage(QWidget):
    refresh_users = Signal()

    def __init__(self, api: CrmApiAsync):
        super().__init__()
        self.api = api
        self.user_table = None
        self.model = None
        self.refresh_users.connect(lambda: asyncio.create_task(self.load_users()))
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

        asyncio.create_task(self.load_users())

        self.user_table = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone", "Action"])
        self.user_table.setModel(self.model)
        self._configure_user_table()
        layout.addWidget(self.user_table, 1)

        self.setLayout(layout)


    async def load_users(self):
        users_data = await self.api.get_all_users()
        if "err" in users_data:
            users_data = await self.api.get_all_users()

        self.model.removeRows(0, self.model.rowCount())

        for user in users_data:
            user_id = str(user["id"])
            print(user, "L.80, ViewUserPage.py")
            users = [
                QStandardItem(str(user["id"])),
                QStandardItem(user["name"]),
                QStandardItem(user["first_name"]),
                QStandardItem(user["email"]),
                QStandardItem(user["telephone"]),
            ]
            self.model.appendRow(users)

            # ---- Création des boutons ----
            index = self.model.index(self.model.rowCount() - 1, 5)

            # Conteneur horizontal
            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)

            # Bouton Modifier
            btn_edit = QPushButton("✏️ Modifier")
            btn_edit.setObjectName("btn_edit")
            btn_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_edit.clicked.connect(lambda _, uid=user_id: asyncio.create_task(self.update_user(uid)))

            # Bouton Supprimer
            btn_delete = QPushButton("🗑 Supprimer")
            btn_delete.setObjectName("btn_delete")
            btn_delete.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_delete.clicked.connect(lambda _, uid=user_id: asyncio.create_task(self.delete_user(uid)))

            layout.addWidget(btn_edit)
            layout.addWidget(btn_delete)

            self.user_table.setIndexWidget(index, action_widget)


    # ------------------------------------------------
    #   Fonction pour supprimer un utilisateur.
    # ------------------------------------------------

    async def delete_user(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer l’utilisateur {user_id} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            result = await self.api.delete_user(user_id)
            print("delete !")
            if "err" in result:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l’utilisateur {user_id}")
            else:
                await self.load_users()
                QMessageBox.information(self, "Succès", f"Utilisateur {user_id} supprimé")

    # ------------------------------------------------
    #   Fonction pour modifier un utilisateur.
    # ------------------------------------------------

    async def update_user(self, user_id):
        """Passe la ligne de l'utilisateur en mode édition"""
        print(f"Modification de l'utilisateur {user_id}")

        # Trouver la ligne correspondant à l'utilisateur
        row = None
        for r in range(self.model.rowCount()):
            if self.model.item(r, 0).text() == str(user_id):
                row = r
                break

        if row is None:
            return

        # Récupération des données existantes
        name = self.model.item(row, 1).text()
        first_name = self.model.item(row, 2).text()
        email = self.model.item(row, 3).text()
        telephone = self.model.item(row, 4).text()

        # Crée des champs éditables
        name_edit = QLineEdit(name)
        first_name_edit = QLineEdit(first_name)
        email_edit = QLineEdit(email)
        telephone_edit = QLineEdit(telephone)

        # Remplace les cellules par des widgets
        self.user_table.setIndexWidget(self.model.index(row, 1), name_edit)
        self.user_table.setIndexWidget(self.model.index(row, 2), first_name_edit)
        self.user_table.setIndexWidget(self.model.index(row, 3), email_edit)
        self.user_table.setIndexWidget(self.model.index(row, 4), telephone_edit)

        # Colonne Action : bouton "Enregistrer"
        index_action = self.model.index(row, 5)
        save_widget = QWidget()
        layout = QHBoxLayout(save_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setObjectName("btn_save")
        btn_save.setFocusPolicy(Qt.FocusPolicy.NoFocus)


        # Au clic → envoyer les nouvelles données à l’API
        async def save_changes():
            new_data = {
                "name": name_edit.text(),
                "first_name": first_name_edit.text(),
                "email": email_edit.text(),
                "telephone": telephone_edit.text(),
            }
            print("Nouvelles données :", new_data)

            result = await self.api.update_user(user_id, new_data)
            if isinstance(result, dict) and "err" in result:
                print("❌ Erreur :", result["err"])
            else:
                print("✅ Modifié avec succès !")
                # Recharge la ligne pour repasser en mode lecture
                await self.load_users()

        btn_save.clicked.connect(lambda _: asyncio.create_task(save_changes()))

        layout.addWidget(btn_save)
        self.user_table.setIndexWidget(index_action, save_widget)



    def _configure_user_table(self):
        self.user_table.setColumnWidth(3, 225)
        self.user_table.setColumnWidth(4, 150)
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
        self.user_table.setStyleSheet(load_qss_file("user_table.qss"))