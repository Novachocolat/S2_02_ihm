# ==============================================================
# Fenêtre de licence de l'application Market Tracer
# Développé par D. MELOCCO, S. LECLERCQ-SPETER
# Dernière modification : 13/06/2025
# ==============================================================

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QTextEdit
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

class LicenceWindow(QWidget):
    """Fenêtre de licence de l'application Market Tracer."""
    def __init__(self):
        """Initialisation de la fenêtre de licence."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Licence")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre de licence."""

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("img/logo_ext_v1.png")
        pixmap = pixmap.scaled(400, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo)

        # Paragraphe déroulant
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        licence_text = QTextEdit()
        licence_text.setReadOnly(True)
        licence_text.setFont(QFont("Arial", 10))

        # Charger le contenu du fichier LICENCE
        try:
            with open("LICENCE", "r", encoding="utf-8") as f:
                licence_content = f.read()
        except Exception as e:
            licence_content = f"Impossible de charger le fichier LICENCE : {e}"
        licence_text.setPlainText(licence_content)
        
        scroll.setWidget(licence_text)
        main_layout.addWidget(scroll)