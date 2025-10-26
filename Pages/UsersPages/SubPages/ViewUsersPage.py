"""
ViewUserPage.py
===============

Module de la classe contenant la page ViewUserPage.

Dependencies:
    pyside6: Module principal du programme.
"""

import asyncio

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QPushButton, QMessageBox, QHBoxLayout, QLineEdit

from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file


class ViewUserPage(QWidget):
    """Classe contenant la page ViewUserPage.

    Cette classe hérite de QWidget.

    Attributes:
        refresh_users (Signal): Signal permettant de mettre à jour le tableau des utilisateurs.
        api (CrmApiAsync): Classe contenant les requêtes API client.
        user_table (QTreeView): Le tableau des utilisateurs.
        model (QStandardItemModel): Le model du tableau.
        info_label (QLabel): Le label informant d'éventuelle erreur.
    """
    refresh_users = Signal()

    def __init__(self, api: CrmApiAsync):
        """Constructeur de la classe ViewUserPage.

        Args:
            api (CrmApiAsync): Classe contenant les requêtes API client.
        """
        super().__init__()
        self.api = api
        self.user_table = None
        self.model = None
        self.info_label = None
        self.refresh_users.connect(lambda: asyncio.create_task(self.load_users()))
        self.init_ui()

    def init_ui(self):
        """
        Initialisation de l'interface graphique de la page ViewUserPage.
        """
        layout = QVBoxLayout()
        title = QLabel("Les utilisateurs", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""font-size: 24px; padding: 20;""")
        layout.addWidget(title)

        self.user_table = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone", "Action"])
        self.user_table.setModel(self.model)
        self._configure_user_table()
        layout.addWidget(self.user_table, 1)

        self.info_label = QLabel()
        self.info_label.setStyleSheet("""font-size: 24px; padding: 20; color: red;""")
        layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.load_users())

        self.setLayout(layout)

    async def load_users(self):
        """
        Méthode permettant de mettre à jour ou de charger les utilisateurs.
        """
        requests_users_data = await self.api.get_all_users()
        requests_code = await self.api.verify_request(requests_users_data)

        self.model.removeRows(0, self.model.rowCount())

        if requests_code == self.api.Ok:
            self._add_users(requests_users_data)
        elif requests_code == self.api.UserReconnected:
            self._add_users(requests_users_data)
        elif requests_code == self.api.AccessTokenError:
            QMessageBox.critical(self, "Erreur", f"Votre connexion a expiré ! Veuillez vous reconnecter !")
            self.info_label.setText("Votre connexion a expiré ! Veuillez vous reconnecter !")
        elif requests_code == self.api.OtherError:
            if requests_users_data["err"].message == "Not authenticated":
                self.info_label.setText("Vous n'êtes pas connecté !")
        elif requests_code == self.api.ErrorNotFound:
            self.info_label.setText("Un problème est survenu, veuillez contacté l'administrateur de ce programme !")

    def _add_button_to_table(self, name: str, object_name: str, layout: QHBoxLayout, user_id: int, action):
        btn = QPushButton(name)
        btn.setObjectName(object_name)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.clicked.connect(lambda _, uid=user_id: asyncio.create_task(action(uid)))
        layout.addWidget(btn)

    def _add_user_to_table(self, user: dict):
        print(user, "L.80, ViewUserPage.py")
        if user == "err":
            self.info_label.setText("Une erreur est survenue, veuillez relancer l'application !")
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

        self._add_button_to_table("✏️ Modifier", "btn_edit", layout, user["id"], self.update_user)
        self._add_button_to_table("🗑 Supprimer", "btn_delete", layout, user["id"], self.delete_user)

        self.user_table.setIndexWidget(index, action_widget)

    def _add_users(self, users: dict):
        for user in users:
            self._add_user_to_table(user)

    # ------------------------------------------------
    #   Méthode pour supprimer un utilisateur.
    # ------------------------------------------------

    async def delete_user(self, user_id: int):
        """Méthode permettant de supprimer un utilisateur.

        Args:
            user_id (int): ID de l'utilisateur à supprimer.
        """
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
                await self.load_users()
                # QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l’utilisateur {user_id}")
            else:
                await self.load_users()
                QMessageBox.information(self, "Succès", f"Utilisateur {user_id} supprimé")

    # ------------------------------------------------
    #   Méthode pour modifier un utilisateur.
    # ------------------------------------------------

    async def update_user(self, user_id: int):
        """Méthode permettant de modifier un utilisateur sur le tableau.

        Args:
            user_id (int): ID de l'utilisateur à modifier.
        """
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
        """
        Méthode qui configure le tableau des utilisateurs
        """
        self.user_table.setColumnWidth(3, 225)
        self.user_table.setColumnWidth(4, 150)
        self.user_table.setColumnWidth(5, 150)
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
