"""
ViewUserPage.py
===============

Module de la classe contenant la page ViewUserPage.

Dependencies:
    pyside6: Module principal du programme.
"""

import asyncio

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QPushButton, QMessageBox, QHBoxLayout, QLineEdit

from utils.CrmApiAsync import CrmApiAsync
from utils.utils import load_qss_file, create_message_box, configure_line_edit, get_icon


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
        Constructeur de l'interface graphique de la page ViewUserPage.
        """
        layout = QVBoxLayout()
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)

        title = QLabel("Les utilisateurs", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""font-size: 24px; padding: 20;""")

        title_layout.addWidget(title)
        title_layout.addStretch()
        add_button_to_layout("", "", title_layout, self.load_users, get_icon("actualise.png"))

        layout.addWidget(title_container)

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
            for user in requests_users_data:
                self._add_user_to_table(user)
        elif requests_code == self.api.AccessTokenError:
            QMessageBox.critical(self, "Erreur", f"Votre connexion a expiré ! Veuillez vous reconnecter !")
            self.info_label.setText("Votre connexion a expiré ! Veuillez vous reconnecter !")
        elif requests_code == self.api.OtherError:
            if requests_users_data["err"].message == "Not authenticated":
                self.info_label.setText("Vous n'êtes pas connecté !")
        elif requests_code == self.api.ErrorNotFound:
            self.info_label.setText("Un problème est survenu, veuillez contacté l'administrateur de ce programme !")

    def _add_user_to_table(self, user: dict):
        """Méthode permettant d'ajouter un utilisateur dans le tableau.

        Args:
            user (dict): L'utilisateur à ajouter.
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

        # ---- Création des boutons ----
        index = self.model.index(self.model.rowCount() - 1, 5)

        # Conteneur horizontal
        action_widget = QWidget()
        layout = QHBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        add_button_to_layout(name="✏️ Modifier", object_name="btn_edit", layout=layout, action=self.update_user, user_id=user["id"])
        add_button_to_layout(name="🗑 Supprimer", object_name="btn_delete", layout=layout, action=self.delete_user, user_id=user["id"])

        self.user_table.setIndexWidget(index, action_widget)

    # ------------------------------------------------
    #   Méthode pour supprimer un utilisateur.
    # ------------------------------------------------

    async def delete_user(self, user_id: int):
        """Méthode permettant la suppression de l'utilisateur.

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
            elif result_code == self.api.AccessTokenError:
                create_message_box(self, "Erreur", "Votre connexion a expiré ! Veuillez vous reconnecter !", False,
                                   True)
            elif result_code == self.api.OtherError:
                print(result, "ViewUserPage.py | L.161")
                create_message_box(self, "Erreur",
                                   f"Une erreur a été rencontrée lors de la suppression de l'utilisateur !",
                                   False, True)
            elif result_code == self.api.ErrorNotFound:
                print(result, "ViewUserPage.py | L.164")
                create_message_box(self, "Erreur", f"L'utilisateur n'a pas pu être supprimé !", False, True)

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

        configure_line_edit(name_edit, first_name_edit, telephone_edit, email_edit)

        # Remplace les cellules par des widgets
        colonne = 0
        for edit in [name_edit, first_name_edit, email_edit, telephone_edit]:
            edit.setStyleSheet("font-size: 17px;")
            colonne += 1
            self.user_table.setIndexWidget(self.model.index(row, colonne), edit)

        # Colonne Action : bouton "Enregistrer"
        index_action = self.model.index(row, 5)
        save_widget = QWidget()
        layout = QHBoxLayout(save_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Au clic → envoyer les nouvelles données à l’API
        async def save_changes():
            """
            Fonction interne à la méthode update_user gérant la requête pour modifier l'utilisateur côté base de donnée.
            """
            new_data = {
                "name": name_edit.text(),
                "first_name": first_name_edit.text(),
                "email": email_edit.text(),
                "telephone": telephone_edit.text(),
            }
            print("Nouvelles données :", new_data)

            result = await self.api.update_user(user_id, new_data)
            result_code = await self.api.verify_request(result)

            # Vérification de la requête.
            if result_code == self.api.Ok:
                await self.load_users()
                print("Modification réussi !")
            elif result_code == self.api.AccessTokenError:
                create_message_box(self, "Erreur", "Votre connexion a expiré ! Veuillez vous reconnecter !", False,
                                   True)
                await self.load_users()
            elif result_code == self.api.OtherError:
                print(result, "ViewUserPage.py | L.251")
                if result["err"].message == "User already exists!":
                    create_message_box(self, "Erreur",
                                       "La modification que vous tentez de faire est déjà attribué à un utilisateur !",
                                       False, True)
                else:
                    print(result, "ViewUserPage.py | L.255")
                    create_message_box(self, "Erreur", "Une erreur inattendu a été détecté !", False,
                                       True)
                await self.load_users()
            elif result_code == self.api.ErrorNotFound:
                create_message_box(self, "Erreur", "Une erreur inattendu a été détecté !", False,
                                   True)
                await self.load_users()

        add_button_to_layout(name="💾 Enregistrer", object_name="btn_save", layout=layout, action=save_changes)

        self.user_table.setIndexWidget(index_action, save_widget)

    def _configure_user_table(self):
        """
        Méthode qui configure le tableau des utilisateurs.
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


# ------------------------------------------------
#   Fonction utilitaire.
# ------------------------------------------------
def add_button_to_layout(name: str, object_name: str, layout: QHBoxLayout, action, icon: QIcon = None, user_id: int = 0):
    """Fonction pour ajouter un bouton dans un layout.

    Args:
        name (str): Nom du bouton.
        object_name (str): Nom du style du bouton.
        layout (QHBoxLayout): Le layout dont le bouton a été ajouté.
        action: Action du bouton.
        icon (QIcon): Optionnel, Icon du bouton.
        user_id (int): Optionnel, ID de l'utilisateur de la ligne du bouton.
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
