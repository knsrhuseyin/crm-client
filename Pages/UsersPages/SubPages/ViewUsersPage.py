"""
ViewUserPage.py
===============

Module contenant la page ViewUserPage pour la gestion des utilisateurs.

Dependencies:
    PySide6: Pour la création de l'interface graphique.
    asyncio: Pour la gestion des tâches asynchrones.
"""

import asyncio
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QPushButton, QMessageBox, QHBoxLayout, QLineEdit

from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, create_message_box, configure_line_edit, get_icon


class ViewUserPage(QWidget):
    """Page affichant la liste des utilisateurs avec possibilité de modifier ou supprimer.

    Hérite de QWidget.

    Attributes:
        refresh_users (Signal): Signal pour rafraîchir la liste des utilisateurs.
        api (CrmApiAsync): Client API pour la communication avec le backend.
        user_table (QTreeView): Tableau affichant les utilisateurs.
        model (QStandardItemModel): Modèle du tableau.
        info_label (QLabel): Label d'information pour les erreurs ou messages.
    """
    refresh_users = Signal()

    def __init__(self, api: CrmApiAsync):
        """Initialise la page ViewUserPage.

        Args:
            api (CrmApiAsync): Client API.
        """
        super().__init__()
        self.api = api
        self.user_table = None
        self.model = None
        self.info_label = None
        self.refresh_users.connect(lambda: asyncio.create_task(self.load_users()))
        self.init_ui()

    def init_ui(self):
        """Construit l'interface graphique de la page ViewUserPage."""
        layout = QVBoxLayout()

        # En-tête avec titre et bouton actualiser
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title = QLabel("Les utilisateurs", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; padding: 20;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        add_button_to_layout("", "", title_layout, self.load_users, get_icon("actualise.png"))
        layout.addWidget(title_container)

        # Tableau des utilisateurs
        self.user_table = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone", "Action"])
        self.user_table.setModel(self.model)
        self._configure_user_table()
        layout.addWidget(self.user_table, 1)

        # Label d'information
        self.info_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 24px; padding: 20; color: red;")
        layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.load_users())
        self.setLayout(layout)

    async def load_users(self):
        """Charge ou met à jour la liste des utilisateurs depuis l'API."""
        requests_users_data = await self.api.get_all_users()
        requests_code = await self.api.verify_request(requests_users_data)

        self.model.removeRows(0, self.model.rowCount())

        if requests_code == self.api.Ok:
            self.info_label.setText("")
            for user in requests_users_data:
                self._add_user_to_table(user)
        elif requests_code == self.api.ErrorDNS:
            create_message_box(self, "Erreur de connexion", "Veuillez vérifiez votre connexion internet !", False)
            self.info_label.setText("Erreur de connexion\nVeuillez vérifiez votre connexion internet !")
        elif requests_code == self.api.AccessTokenError:
            create_message_box(self, "Erreur", "Votre connexion a expiré ! Veuillez vous reconnecter !", False)
            self.info_label.setText("Votre connexion a expiré\nVeuillez vous reconnecter !")
        elif requests_code == self.api.OtherError and requests_users_data["err"].message == "Not authenticated":
            self.info_label.setText("Vous n'êtes pas connecté !")
        elif requests_code == self.api.ErrorNotFound:
            self.info_label.setText("Un problème est survenu, veuillez contacter l'administrateur !")

    def _add_user_to_table(self, user: dict):
        """Ajoute un utilisateur dans le tableau avec les boutons Modifier et Supprimer.

        Args:
            user (dict): Dictionnaire contenant les informations de l'utilisateur.
        """
        if user == "err":
            self.info_label.setText("Une erreur est survenue, veuillez relancer l'application !")
            return

        users = [
            QStandardItem(str(user["id"])),
            QStandardItem(user["name"]),
            QStandardItem(user["first_name"]),
            QStandardItem(user["email"]),
            QStandardItem(user["telephone"]),
        ]
        self.model.appendRow(users)

        # Ajout des boutons dans la colonne Action
        index = self.model.index(self.model.rowCount() - 1, 5)
        action_widget = QWidget()
        layout = QHBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        add_button_to_layout("✏️ Modifier", "btn_edit", layout, self.update_user, user_id=user["id"])
        add_button_to_layout("🗑 Supprimer", "btn_delete", layout, self.delete_user, user_id=user["id"])

        self.user_table.setIndexWidget(index, action_widget)

    async def delete_user(self, user_id: int):
        """Supprime un utilisateur après confirmation.

        Args:
            user_id (int): ID de l'utilisateur à supprimer.
        """
        confirm = create_message_box(self, "Confirmation",
                                     f"Voulez-vous vraiment supprimer l’utilisateur {user_id} ?",
                                     True)
        if confirm:
            result = await self.api.delete_user(user_id)
            result_code = await self.api.verify_request(result)

            if result_code == self.api.Ok:
                await self.load_users()
                create_message_box(self, "Succès", f"Utilisateur {user_id} supprimé")
            elif result_code == self.api.ErrorDNS:
                create_message_box(self, "Erreur de connexion", "Veuillez vérifiez votre connexion internet !", False)
            elif result_code == self.api.AccessTokenError:
                create_message_box(self, "Erreur", "Votre connexion a expiré ! Veuillez vous reconnecter !", False, True)
            else:
                create_message_box(self, "Erreur", f"L'utilisateur n'a pas pu être supprimé !", False, True)

    async def update_user(self, user_id: int):
        """Permet de modifier un utilisateur directement dans le tableau.

        Args:
            user_id (int): ID de l'utilisateur à modifier.
        """
        # Recherche de la ligne correspondant à l'utilisateur
        row = next((r for r in range(self.model.rowCount()) if self.model.item(r, 0).text() == str(user_id)), None)
        if row is None:
            return

        # Récupération des données existantes
        name = self.model.item(row, 1).text()
        first_name = self.model.item(row, 2).text()
        email = self.model.item(row, 3).text()
        telephone = self.model.item(row, 4).text()

        # Champs éditables
        name_edit = QLineEdit(name)
        first_name_edit = QLineEdit(first_name)
        email_edit = QLineEdit(email)
        telephone_edit = QLineEdit(telephone)
        configure_line_edit(name_edit, first_name_edit, telephone_edit, email_edit)

        for col, edit in enumerate([name_edit, first_name_edit, email_edit, telephone_edit], start=1):
            edit.setStyleSheet("font-size: 17px;")
            self.user_table.setIndexWidget(self.model.index(row, col), edit)

        # Bouton "Enregistrer"
        index_action = self.model.index(row, 5)
        save_widget = QWidget()
        layout = QHBoxLayout(save_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        async def save_changes():
            """Envoie les nouvelles données à l'API pour mise à jour."""
            new_data = {
                "name": name_edit.text(),
                "first_name": first_name_edit.text(),
                "email": email_edit.text(),
                "telephone": telephone_edit.text(),
            }
            result = await self.api.update_user(user_id, new_data)
            result_code = await self.api.verify_request(result)
            if result_code == self.api.Ok:
                await self.load_users()
            else:
                await self.load_users()  # Rechargement pour éviter les données corrompues
                create_message_box(self, "Erreur", "Une erreur est survenue lors de la modification !", False)

        add_button_to_layout("💾 Enregistrer", "btn_save", layout, save_changes)
        self.user_table.setIndexWidget(index_action, save_widget)

    def _configure_user_table(self):
        """Configure l'affichage et le comportement du tableau des utilisateurs."""
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


# ------------------------------------------------
# Fonction utilitaire
# ------------------------------------------------
def add_button_to_layout(name: str, object_name: str, layout: QHBoxLayout, action, icon: QIcon = None, user_id: int = 0):
    """Ajoute un bouton dans un layout horizontal.

    Args:
        name (str): Texte du bouton.
        object_name (str): Nom pour le style du bouton.
        layout (QHBoxLayout): Layout où ajouter le bouton.
        action: Fonction appelée au clic (async).
        icon (QIcon, optional): Icône du bouton.
        user_id (int, optional): ID utilisateur lié à l'action.
    """
    btn = QPushButton(name)
    btn.setObjectName(object_name)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    if icon is not None:
        btn.setIcon(icon)
        btn.setIconSize(QSize(50, 50))
    if user_id == 0:
        btn.clicked.connect(lambda: asyncio.create_task(action()))
    else:
        btn.clicked.connect(lambda _, uid=user_id: asyncio.create_task(action(uid)))
    layout.addWidget(btn)
