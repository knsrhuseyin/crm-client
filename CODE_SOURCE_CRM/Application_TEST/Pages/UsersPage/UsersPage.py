# Page Utilisateurs
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QPushButton, QHBoxLayout
from CODE_SOURCE_CRM.Application_TEST.Pages.UsersPage.style import user_page_style


class ListUsers(QWidget):
    def __init__(self, bdd, main_layout):
        super().__init__()
        self.bdd = bdd

        # --- Titre ---
        title = QLabel("<h2>Gestion des utilisateurs</h2>", alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # --- Tableau dynamique avec QTreeView ---
        self.user_table = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone", "Mot de passe"])

        # Exemple d’utilisateurs
        test = self.bdd.get_users_on_sql()
        print(test)
        users = test

        for id, name, first_name, email, tel, password in users:
            items = [
                QStandardItem(str(id)),
                QStandardItem(name),
                QStandardItem(first_name),
                QStandardItem(email),
                QStandardItem(str(tel)),
                QStandardItem(password)
            ]
            for item in items:
                item.setEditable(False)  # pas éditable directement
            self.model.appendRow(items)

        self.user_table.setModel(self.model)
        self.user_table.setRootIsDecorated(False)  # pas de hiérarchie visible
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.user_table.setSortingEnabled(True)
        self.user_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Ajouter le tableau avec stretch pour prendre tout l’espace restant
        main_layout.addWidget(self.user_table, 1)

        # --- Bouton Ajouter utilisateur ---
        self.add_button = QPushButton("Ajouter un utilisateur")
        self.add_button.setFixedWidth(200)  # taille fixe
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self.add_user)

        # Centrer le bouton horizontalement
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # --- Appliquer le layout ---
        self.setLayout(main_layout)

        # --- Style bleu sombre ---
        self.setStyleSheet(user_page_style)


class UsersPage(QWidget):
    def __init__(self, bdd):
        super().__init__()
        self.bdd = bdd

        # --- Layout principal ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)



    def add_user(self):
        add_user(self.bdd)