# ==============================================================

# Market Tracer - Documentation
# Développée par David Melocco et Simon Leclercq-Speter
# Dernière modification : 11/06/2025

# ==============================================================

# Importations
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QTextBrowser
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

# ==============================================================
# Fenêtre de documentation de l'application Market Tracer
# ==============================================================
class DocWindow(QWidget):
    """Fenêtre de documentation de l'application Market Tracer.

    Args:
        QWidget (QWidget): classe de base pour les widgets de l'interface graphique.
    """
    def __init__(self):
        """Initialisation de la fenêtre de documentation."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Documentation")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre de documentation."""
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

        # Paragraphe déroulant avec rendu Markdown
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        doc_browser = QTextBrowser()
        doc_browser.setReadOnly(True)
        try:
            with open("DOC.md", encoding="utf-8") as f:
                readme_content = f.read()
        except Exception as e:
            html_content = "<b>README.md introuvable ou erreur de lecture.</b><br><br>" + str(e)
        doc_browser.setHtml(html_content)
        scroll.setWidget(doc_browser)
        main_layout.addWidget(scroll)

# ==============================================================
# Exécution du programme pour débogage
# ==============================================================
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = DocWindow()
#     win.show()
#     sys.exit(app.exec())