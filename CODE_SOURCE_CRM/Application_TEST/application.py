import sys
from PySide6.QtWidgets import (
    QApplication, QStackedWidget, QListWidget, QListWidgetItem, QHBoxLayout
)

from CODE_SOURCE_CRM.Application_TEST.Pages.UsersPage.UsersPage import UsersPage
from CODE_SOURCE_CRM.Database.database import DataBase
from Pages_1 import *

# -------------------------------
# Classe MenuWidget
# -------------------------------
class MenuWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.addItem(QListWidgetItem("🏠 Accueil"))
        self.addItem(QListWidgetItem("👥 Utilisateurs"))
        self.addItem(QListWidgetItem("⚙️ Paramètres"))
        self.setCurrentRow(0)


# -------------------------------
# Classe AdminPanel
# -------------------------------
class AdminPanel(QWidget):
    def __init__(self, bdd: DataBase):
        super().__init__()
        self.bdd = bdd

        # --- Menu ---
        self.menu = MenuWidget()

        # --- Contenu (Stack) ---
        self.stack = QStackedWidget()
        self.stack.addWidget(HomePage())
        self.stack.addWidget(UsersPage(self.bdd))
        self.stack.addWidget(SettingsPage())

        # --- Layout principal ---
        layout = QHBoxLayout()
        layout.addWidget(self.menu)
        layout.addWidget(self.stack, 1)
        self.setLayout(layout)

        # Connexion menu → stack
        self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)

        # --- Fenêtre ---
        self.setWindowTitle("Admin Panel - Thème Bleu Sombre")
        self.resize(1280, 720)

        # --- Style centralisé ---
        self.setStyleSheet(self.get_stylesheet())

    # Méthode pour centraliser le style
    @staticmethod
    def get_stylesheet() -> str:
        return """
        QWidget {
            background-color: #0f172a;
            font-family: Segoe UI, sans-serif;
            font-size: 14px;
            border: none;
        }
        QFrame, QListView, QStackedWidget {
            border: none;
            background: transparent;
        }
        QListWidget {
            background-color: #1e3a8a;
            color: white;
            border: none;
            padding: 10px;
        }
        QListWidget::item {
            padding: 12px;
            margin: 4px 0;
            border-radius: 6px;
        }
        QListWidget::item:selected {
            background-color: #2563eb;
            font-weight: bold;
        }
        QLabel {
            color: white;
            border: none;
        }
        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
        QPushButton:pressed {
            background-color: #1e40af;
        }
        """


# -------------------------------
# Lancer l'application
# -------------------------------



if __name__ == "__main__":
    connection_params = {
        'host': "localhost",
        'user': "root",
        'password': "Huseyin200819",
        'database': "bdd"
    }
    bdd = DataBase(**connection_params)
    app = QApplication(sys.argv)
    window = AdminPanel(bdd)
    #window = None
    window.resize(1280, 720)
    window.show()
    sys.exit(app.exec())


