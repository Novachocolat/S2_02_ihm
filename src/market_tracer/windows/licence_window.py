# ==============================================================
# Fenêtre de licence de l'application Market Tracer
# Développé par D. MELOCCO, S. LECLERCQ-SPETER
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QScrollArea, QTextEdit, QVBoxLayout, QWidget

from market_tracer.paths import LICENCE_PATH
from market_tracer.ui_helpers import app_icon, logo_label


class LicenceWindow(QWidget):
    """Fenêtre de licence de l'application Market Tracer."""
    def __init__(self):
        """Initialisation de la fenêtre de licence."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Licence")
        self.setWindowIcon(app_icon())
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre de licence."""

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Logo
        main_layout.addWidget(logo_label())

        # Paragraphe déroulant
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        licence_text = QTextEdit()
        licence_text.setReadOnly(True)
        licence_text.setFont(QFont("Arial", 10))

        # Charger le contenu du fichier LICENCE
        try:
            with open(LICENCE_PATH, "r", encoding="utf-8") as f:
                licence_content = f.read()
        except Exception as e:
            licence_content = f"Impossible de charger le fichier LICENCE : {e}"
        licence_text.setPlainText(licence_content)

        scroll.setWidget(licence_text)
        main_layout.addWidget(scroll)
