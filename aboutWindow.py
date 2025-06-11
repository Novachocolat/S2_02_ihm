# ==============================================================

# Market Tracer - À propos
# Développée par D. Melocco / S.Leclercq-Speter
# Dernière modification : 11/06/2025 17h54

# ==============================================================

# Importations
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

# ==============================================================
# Page À propos

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - À propos")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        # Layout principal vertical
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
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # centre horizontal et vertical
        main_layout.addWidget(version_label)

        # Description
        desc = QLabel(
            "Market Tracer est un outil compétent qui aide à la \n"
            "gestion des stocks des supermarchés et qui permet\n"
            "à leurs clients fidèles de faire leurs courses efficacement\n\n"
            "Ce Logiciel a été développé par :\n"
            "D. Melocco / L. Pace--Boulnois / S. Leclercq-Speter / N. Colin \n"
        )
        desc.setFont(QFont("Arial", 12))
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)  # centre horizontal et vertical
        main_layout.addWidget(desc)

# ==============================================================
# Mise en route de l'application
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AboutWindow()
    win.show()
    sys.exit(app.exec())