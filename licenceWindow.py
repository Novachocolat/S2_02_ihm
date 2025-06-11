# ==============================================================

# Market Tracer - Licence
# Développée par D. Melocco
# Dernière modification : 11/06/2025

# ==============================================================

# Importations
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QTextEdit
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

# ==============================================================
# Page Licence

class LicenceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Licence")
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
        version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(version_label)

        # Paragraphe déroulant
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        licence_text = QTextEdit()
        licence_text.setReadOnly(True)
        licence_text.setFont(QFont("Arial", 10))
        licence_text.setPlainText(
            "Licence à écrire..\n"
        )
        scroll.setWidget(licence_text)
        main_layout.addWidget(scroll)

# ==============================================================
# Mise en route de l'application
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LicenceWindow()
    win.show()
    sys.exit(app.exec())