from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)


# Page Accueil
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("<h2>Bienvenue 👋</h2>", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addStretch()  # pousse le bouton en bas
        layout.addWidget(QPushButton("Action rapide"))

        self.setLayout(layout)


# Page Paramètres
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("<h2>Paramètres système</h2>", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addStretch()
        layout.addWidget(QPushButton("Sauvegarder"))

        self.setLayout(layout)
