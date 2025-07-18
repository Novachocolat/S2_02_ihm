# ==============================================================
# Fenêtre À propos de l'application Market Tracer
# Développé par D. MELOCCO, S. LECLERCQ-SPETER
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

class AboutWindow(QWidget):
    """Fenêtre À propos de l'application Market Tracer."""
    def __init__(self):
        """Initialisation de la fenêtre À propos."""
        super().__init__()
        self.setWindowTitle("Market Tracer - À propos")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre À propos."""

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

        # Version du logiciel
        version_label = QLabel("Version 1")
        version_label.setFont(QFont("Arial", 12))
        version_label.setStyleSheet("color: #888;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        main_layout.addWidget(version_label)

        # Description
        desc = QLabel(
            "Market Tracer est un outil compétent qui aide à la \n"
            "gestion des stocks des supermarchés et qui permet\n"
            "à leurs clients fidèles de faire leurs courses efficacement.\n\n"
        )
        desc.setFont(QFont("Arial", 12))
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        main_layout.addWidget(desc)

        # Auteurs
        authors = QLabel(
            "David Melocco\n"
            "Lysandre Pace--Boulnois\n"
            "Simon Leclercq-Speter\n"
            "Noé Colin"
        )
        authors.setFont(QFont("Arial", 12))
        authors.setAlignment(Qt.AlignmentFlag.AlignLeft)
        authors.setStyleSheet("color: #555;")
        main_layout.addWidget(authors)