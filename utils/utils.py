"""
utils.py
========

Ce module ajoute des fonctions utilitaires pour mieux gérer le style ou faciliter certaines répétitions.

Dependencies:
    pyside6: Module principal du programme
    json: Pour manipuler des fichiers json
"""

# import module
import json
import os
# import module python
from pathlib import Path
from typing import List

# import classes pyside6
from PySide6.QtGui import QGuiApplication
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


def center_on_screen(self):
    """
    Fonction permettant de centrer la page sur l'écran
    """
    screen = QGuiApplication.primaryScreen().availableGeometry()
    x = (screen.width() - self.width()) // 2
    y = (screen.height() - self.height()) // 2
    self.move(x, y)


def update_json_file(file_path: str, key: str, value):
    """Fonction permettant de mettre à jour un json en lui ajoutant une valeur via une clé

    Args:
        file_path (str): Destination du fichier json.
        key (str): Clé de la valeur à modifier.
        value: La nouvelle valeur.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    with open(file_path, "r") as f:
        json_file = json.load(f)

    json_file[key] = value

    with open(file_path, "w") as f:
        json.dump(json_file, f, indent=4, ensure_ascii=False)


def get_key_data_json(file_path: str, key: str):
    """Fonction permettant de récupérer une valeur par rapport au clé donnée dans le fichier json

    Args:
        file_path (str): Destination du fichier json.
        key (str): La clé de la valeur à récupérer.
    """
    if not os.path.exists(file_path):
        print("Fichier inexistant")
        return None
    with open(file_path, "r") as f:
        json_file = json.load(f)
    if key in json_file:
        return json_file[key]
    return None


def get_data_json(file_path: str):
    """Fonction permettant de récupérer les données d'un fichier json.

    Args:
        file_path (str): Destination du fichier json.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(e)
            return None
