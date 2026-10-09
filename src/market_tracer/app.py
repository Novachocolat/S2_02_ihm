# ==============================================================
# Point d'entrée de l'application
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# ==============================================================

import sys

from PyQt6.QtWidgets import QApplication

from market_tracer.controllers.login_controller import LoginController
from market_tracer.models.login_model import init_db


def main():
    """Initialise la base de données puis affiche la fenêtre de connexion."""
    init_db()
    app = QApplication(sys.argv)
    controller = LoginController()
    controller.view.show()
    sys.exit(app.exec())
