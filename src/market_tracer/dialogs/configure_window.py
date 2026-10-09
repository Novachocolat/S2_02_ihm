# ==============================================================
#
# Market Tracer - Fenêtre de configuration d'un magasin
# Développé par Lysandre Pace--Boulnois et David Melocco
# Dernière modification : 13/06/2025
#
# ==============================================================

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QDateEdit, QDialog, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout
)

from market_tracer.constants import DATE_FORMAT
from market_tracer.models.shop_model import get_shop_details, save_shop
from market_tracer.paths import BANNER_HORIZONTAL
from market_tracer.ui_helpers import app_icon

IMAGE_FILTER = "Images (*.png *.jpg *.bmp *.jpeg)"
JSON_FILTER = "Fichiers JSON (*.json)"

SAVE_BUTTON_STYLE = """
    QPushButton {
        background: #4be39a;
        color: #fff;
        padding: 10px;
        border-radius: 6px;
        min-width: 120px;
        min-height: 36px;
        font-size: 16px;
    }
    QPushButton:checked {
        border: 2px solid #222;
        background: #111;
        color: #fff;
    }
"""


class ConfigureWindow(QDialog):
    """Classe pour la fenêtre de configuration d'un magasin."""
    def __init__(self, user_id, parent=None):
        """Initialise la fenêtre de configuration d'un magasin."""
        super().__init__(parent)
        self.setWindowTitle("Market Tracer - Configurer un magasin")
        self.setWindowIcon(app_icon())
        self.setFixedSize(500, 600)
        self.user_id = user_id
        self.shop_data = get_shop_details(user_id)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur pour la fenêtre de configuration d'un magasin."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Image
        img_label = QLabel()
        pixmap = QPixmap(str(BANNER_HORIZONTAL))
        pixmap = pixmap.scaled(600, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addWidget(self._build_info_group())
        main_layout.addWidget(self._build_files_group())
        main_layout.addWidget(self._build_about_group())

        # Bouton de sauvegarde
        btn_creer = QPushButton("Sauvegarder")
        btn_creer.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn_creer.clicked.connect(self.finish)
        btn_creer.setStyleSheet(SAVE_BUTTON_STYLE)
        main_layout.addWidget(btn_creer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._fill_from_shop_data()

    def _build_info_group(self):
        """Groupe « Informations générales »."""
        info_group = QGroupBox("Informations générales")
        info_layout = QFormLayout()
        self.nom_input = QLineEdit()
        self.nom_input.setMaxLength(50)
        self.nom_input.setPlaceholderText("Entrez le nom du magasin")
        self.auteur_input = QLineEdit()
        self.auteur_input.setPlaceholderText("Entrez le(s) gestionnaire(s)")
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat(DATE_FORMAT)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        info_layout.addRow("Nom du magasin *", self.nom_input)
        info_layout.addRow("Gestionnaire(s)", self.auteur_input)
        info_layout.addRow("Date de création", self.date_input)
        info_group.setLayout(info_layout)
        return info_group

    def _build_files_group(self):
        """Groupe « Fichiers » (plan, articles, quadrillage)."""
        files_group = QGroupBox("Fichiers")
        files_layout = QFormLayout()
        self.chemin_input = self._add_file_row(
            files_layout, "Plan du magasin (image)", self.browse_file)
        self.json_input = self._add_file_row(
            files_layout, "Articles (.json)", self.browse_json)
        self.plan_json_input = self._add_file_row(
            files_layout, "Quadrillage (.json)", self.browse_plan_json)
        files_group.setLayout(files_layout)
        return files_group

    @staticmethod
    def _add_file_row(form_layout, label, on_browse):
        """Ajoute une ligne « champ en lecture seule + bouton Parcourir » et retourne le champ."""
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        button = QPushButton("Parcourir...")
        button.clicked.connect(on_browse)
        row = QHBoxLayout()
        row.addWidget(line_edit)
        row.addWidget(button)
        form_layout.addRow(label, row)
        return line_edit

    def _build_about_group(self):
        """Groupe « À propos du magasin »."""
        apropos_group = QGroupBox("À propos du magasin")
        apropos_layout = QVBoxLayout()
        self.apropos_input = QTextEdit()
        self.apropos_input.setPlaceholderText("Décrivez votre magasin...")
        apropos_layout.addWidget(self.apropos_input)
        apropos_group.setLayout(apropos_layout)
        return apropos_group

    def _fill_from_shop_data(self):
        """Pré-remplit les champs avec les données du magasin existant."""
        if not self.shop_data:
            return
        self.nom_input.setText(self.shop_data.get("nom", ""))
        self.auteur_input.setText(self.shop_data.get("auteur", ""))
        date_str = self.shop_data.get("date_creation", "")
        if date_str:
            date = QDate.fromString(date_str, DATE_FORMAT)
            if date.isValid():
                self.date_input.setDate(date)
        self.apropos_input.setPlainText(self.shop_data.get("apropos", ""))
        self.chemin_input.setText(self.shop_data.get("chemin", ""))
        self.json_input.setText(self.shop_data.get("articles_json", ""))
        self.plan_json_input.setText(self.shop_data.get("plan_json", ""))

    def finish(self):
        """Enregistre les données du magasin dans la base de données."""
        nom = self.nom_input.text()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom du magasin est obligatoire.")
            return

        save_shop(
            self.user_id,
            nom,
            self.auteur_input.text(),
            self.date_input.date().toString(DATE_FORMAT),
            self.apropos_input.toPlainText(),
            self.chemin_input.text(),
            self.json_input.text(),
            self.plan_json_input.text(),
        )
        self.accept()

    def _browse(self, line_edit, name_filter):
        """Ouvre un sélecteur de fichier et écrit le fichier choisi dans `line_edit`."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter(name_filter)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                line_edit.setText(selected[0])

    def browse_file(self):
        """Ouvre un dialogue pour sélectionner une image du plan du magasin."""
        self._browse(self.chemin_input, IMAGE_FILTER)

    def browse_json(self):
        """Ouvre un dialogue pour sélectionner un fichier JSON d'articles."""
        self._browse(self.json_input, JSON_FILTER)

    def browse_plan_json(self):
        """Ouvre un dialogue pour sélectionner un fichier JSON de plan (quadrillage) du magasin."""
        self._browse(self.plan_json_input, JSON_FILTER)
