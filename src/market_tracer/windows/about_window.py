# ==============================================================
# Fenêtre À propos de l'application Market Tracer
# Développé par D. MELOCCO, S. LECLERCQ-SPETER
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from market_tracer.ui_helpers import app_icon, logo_label


class AboutWindow(QWidget):
    """Fenêtre À propos de l'application Market Tracer."""
    def __init__(self):
        """Initialisation de la fenêtre À propos."""
        super().__init__()
        self.setWindowTitle("Market Tracer - À propos")
        self.setWindowIcon(app_icon())
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre À propos."""

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Logo
        main_layout.addWidget(logo_label())

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
