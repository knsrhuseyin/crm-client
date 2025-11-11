"""
utils.py
========

Ce module fournit des fonctions et classes utilitaires facilitant la gestion
de l'interface graphique, la manipulation de fichiers JSON et le style général
de l'application.

Dependencies:
    PySide6: Bibliothèque principale utilisée pour créer des interfaces graphiques.
    json: Pour manipuler des fichiers JSON.
"""

# Imports standards
import json
import os
from pathlib import Path
from typing import List

# Imports tiers
from PySide6.QtCore import QRegularExpression, QPoint
from PySide6.QtGui import (
    QGuiApplication,
    QRegularExpressionValidator,
    QIcon,
    QPixmap,
    Qt,
)
from PySide6.QtWidgets import QWidget, QBoxLayout, QMessageBox, QLineEdit, QLabel


class DraggableLabel(QLabel):
    """Label permettant de déplacer sa fenêtre parent par glisser-déposer.

    Attributes:
        drag_position (QPoint): Position du curseur relative au coin supérieur gauche
            de la fenêtre lors du clic de la souris.
    """

    def __init__(self, text: str, parent: QWidget) -> None:
        """Initialise le label draggable.

        Args:
            text (str): Texte affiché dans le label.
            parent (QWidget): Widget parent contenant le label.
        """
        super().__init__(text, parent)
        self.drag_position: QPoint = QPoint()
        self.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event) -> None:
        """Gère le clic de la souris pour initier le déplacement.

        Args:
            event (QMouseEvent): Événement de clic de souris.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Déplace la fenêtre si le bouton gauche de la souris est maintenu.

        Args:
            event (QMouseEvent): Événement de déplacement de la souris.
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def load_qss_file(filename: str) -> str:
    """Charge un fichier `.qss` et renvoie son contenu.

    Args:
        filename (str): Nom du fichier `.qss` contenant le style.

    Returns:
        str: Contenu du fichier `.qss`.
    """
    path = Path(__file__).parent.parent / "styles" / filename
    with path.open(encoding="utf-8") as f:
        return f.read()


def add_widgets(layout: QBoxLayout, widgets: List[QWidget]) -> None:
    """Ajoute plusieurs widgets dans un layout.

    Args:
        layout (QBoxLayout): Le layout où les widgets seront ajoutés.
        widgets (List[QWidget]): Liste des widgets à ajouter.
    """
    for widget in widgets:
        layout.addWidget(widget)


def center_on_screen(widget: QWidget) -> None:
    """Centre une fenêtre sur l'écran principal.

    Args:
        widget (QWidget): Fenêtre à centrer.
    """
    screen = QGuiApplication.primaryScreen().availableGeometry()
    x = (screen.width() - widget.width()) // 2
    y = (screen.height() - widget.height()) // 2
    widget.move(x, y)


def update_json_file(file_path: str, key: str, value) -> None:
    """Met à jour un fichier JSON en ajoutant ou modifiant une clé.

    Args:
        file_path (str): Chemin du fichier JSON.
        key (str): Clé à modifier ou ajouter.
        value: Nouvelle valeur à insérer.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    with open(file_path, "r", encoding="utf-8") as f:
        json_file = json.load(f)

    json_file[key] = value

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_file, f, indent=4, ensure_ascii=False)


def get_key_data_json(file_path: str, key: str):
    """Récupère une valeur spécifique dans un fichier JSON à partir d'une clé.

    Args:
        file_path (str): Chemin du fichier JSON.
        key (str): Clé dont on souhaite obtenir la valeur.

    Returns:
        Any | None: Valeur associée à la clé, ou None si non trouvée.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        json_file = json.load(f)

    return json_file.get(key)


def get_data_json(file_path: str):
    """Récupère le contenu complet d’un fichier JSON.

    Args:
        file_path (str): Chemin du fichier JSON.

    Returns:
        dict | None: Données JSON, ou None en cas d'erreur.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(e)
            return None


def create_message_box(
    parent: QWidget, title: str, text: str, question: bool = False, error: bool = False
) -> bool | None:
    """Crée et affiche une boîte de message (QMessageBox).

    Args:
        parent (QWidget): Widget parent.
        title (str): Titre de la boîte de message.
        text (str): Texte du message.
        question (bool, optional): Affiche une boîte de confirmation Oui/Non. Défaut à False.
        error (bool, optional): Affiche une boîte d'erreur. Défaut à False.

    Returns:
        bool | None: True si l'utilisateur confirme, False sinon, ou None pour un message simple.
    """
    if question:
        confirm = QMessageBox.question(
            parent,
            title,
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return confirm == QMessageBox.StandardButton.Yes

    if error:
        QMessageBox.critical(parent, title, text)
    else:
        QMessageBox.information(parent, title, text)

    return None


def configure_line_edit(
    name_edit: QLineEdit,
    first_name_edit: QLineEdit,
    telephone_edit: QLineEdit,
    email_edit: QLineEdit,
) -> None:
    """Configure les champs de saisie (QLineEdit) avec les règles de validation appropriées.

    Args:
        name_edit (QLineEdit): Champ du nom.
        first_name_edit (QLineEdit): Champ du prénom.
        telephone_edit (QLineEdit): Champ du téléphone.
        email_edit (QLineEdit): Champ du courriel.
    """
    validator_num = QRegularExpressionValidator(QRegularExpression(r"[0-9]{0,10}"))
    validator_text = QRegularExpressionValidator(
        QRegularExpression(r"^[A-Za-zÀ-ÿ\s-]*$")
    )
    validator_mail = QRegularExpressionValidator(
        QRegularExpression(r"^[A-Za-z0-9._@-]*$")
    )

    for edit in [name_edit, first_name_edit, telephone_edit, email_edit]:
        if edit == telephone_edit:
            edit.setMaxLength(10)
            edit.setValidator(validator_num)
        elif edit == email_edit:
            edit.setValidator(validator_mail)
            edit.setMaxLength(50)
        else:
            edit.setMaxLength(100)
            edit.setValidator(validator_text)


def get_icon(file_name: str, is_pixmap: bool = False) -> QIcon | QPixmap:
    """Retourne une icône ou une pixmap à partir du dossier `assets`.

    Args:
        file_name (str): Nom du fichier image.
        is_pixmap (bool, optional): Si True, renvoie un QPixmap au lieu d’un QIcon.

    Returns:
        QIcon | QPixmap: L'icône ou la pixmap correspondante.
    """
    image_path = Path(__file__).parent.parent / "assets" / Path(file_name)
    return QPixmap(str(image_path)) if is_pixmap else QIcon(str(image_path))
