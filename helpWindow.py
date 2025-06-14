# ==============================================================
# Fenêtre de documentation de l'application Market Tracer
# Développé par D. MELOCCO, S. LECLERCQ-SPETER
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QTextBrowser
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

class HelpWindow(QWidget):
    """Fenêtre de documentation de l'application Market Tracer."""
    def __init__(self):
        """Initialisation de la fenêtre de documentation."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Aide")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur de la fenêtre de documentation."""

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
        doc_browser = QTextBrowser()
        doc_browser.setReadOnly(True)

        html_content = """
        <h2 style="text-align:center;">Bienvenue sur Market Tracer !</h2>
        <p>
            Cette fenêtre d'aide vous guide dans la prise en main de l'application.<br>
            <br>
            <b>Fonctionnalités principales :</b>
            <ul>
                <li>Créer et gérer votre liste de courses</li>
                <li>Générer un parcours optimisé dans le magasin</li>
                <li>Visualiser le plan du magasin</li>
                <li>Importer et exporter vos listes</li>
                <li>Accéder à des fonctionnalités avancées selon votre rôle (client ou employé)</li>
            </ul>
            <br>
            <b>Comment démarrer ?</b>
            <ol>
                <li>Ajoutez des articles à votre liste de courses via le panneau de gauche.</li>
                <li>Cliquez sur "Générer le parcours" pour obtenir le chemin optimal.</li>
                <li>Utilisez les menus pour importer/exporter vos listes ou accéder à d'autres options.</li>
            </ol>
            <br>
            <i>Pour toute question, consultez cette aide ou contactez un responsable.</i>
        </p>
        <hr>
        <p style="font-size:10pt; color:gray; text-align:center;">
            Application développée dans le cadre du projet SAE S2.02.<br>
            Version : 1.0
        </p>
        """

        doc_browser.setHtml(html_content)
        scroll.setWidget(doc_browser)
        main_layout.addWidget(scroll)