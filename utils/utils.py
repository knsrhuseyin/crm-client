"""
utils.py
========

Ce module ajoute des fonctions utilitaires pour mieux gérer le style ou faciliter certaines répétitions.
"""
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import QWidget, QBoxLayout


def load_qss_file(filename: str) -> str:
    """Charge un fichier .qss et renvoie son contenu.

    Args:
        filename (str): Fichier .qss contenant le style.
    """
    path = Path(__file__).parent.parent / "styles" / filename
    with path.open(encoding="utf-8") as f:
        return f.read()


def add_widgets(layout: QBoxLayout, widgets: List[QWidget]):
    """Permet de faciliter l'ajout de plusieurs widgets.

    Args:
        layout (QBoxLayout): Le layout où les widgets seront ajoutés.
        widgets (List[QWidget]): Liste des widgets.
    """
    for widget in widgets:
        layout.addWidget(widget)
