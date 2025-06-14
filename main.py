# ==============================================================
# Fichier principal de l'application
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# ===============================================================

from PyQt6.QtWidgets import QApplication
import sys
from models.loginModel import init_db
from controllers.loginController import LoginController

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    controller = LoginController()
    controller.view.show()
    sys.exit(app.exec())