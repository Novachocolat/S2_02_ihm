# ==============================================================
#
# Market Tracer - Fenêtre de configuration d'un magasin
# Développé par Lysandre Pace--Boulnois et David Melocco
# Dernière modification : 13/06/2025
#
# ==============================================================

# Importations
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QFileDialog, QDateEdit, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QDate
import sqlite3

# ==============================================================
# Récupération des données du magasin
# ==============================================================
def get_shop_data(user_id):
    """Récupère les données du magasin pour l'utilisateur donné."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("SELECT nom, auteur, date_creation, apropos, chemin, articles_json, plan_json FROM shops WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        shop_data = {
            "nom": row[0] or "",
            "auteur": row[1] or "",
            "date_creation": row[2] or "",
            "apropos": row[3] or "",
            "chemin": row[4] or "",
            "articles_json": row[5] or "",
            "plan_json": row[6] or ""
        }
    else:
        shop_data = {}
    conn.close()
    return shop_data

# ==============================================================
# Fenêtre principale de la configuration d'un magasin
# ==============================================================
class ConfigureWindow(QDialog): 
    """Classe pour la fenêtre de configuration d'un magasin."""
    def __init__(self, user_id, parent=None):
        """Initialise la fenêtre de configuration d'un magasin."""
        super().__init__(parent)
        self.setWindowTitle("Market Tracer - Configurer un magasin")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(500, 600)
        self.user_id = user_id
        self.shop_data = get_shop_data(user_id)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur pour la fenêtre de configuration d'un magasin."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Image
        img_label = QLabel()
        pixmap = QPixmap(f"img/mt_banner_h.png")
        pixmap = pixmap.scaled(600, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Informations générales
        info_group = QGroupBox("Informations générales")
        info_layout = QFormLayout()
        self.nom_input = QLineEdit()
        self.nom_input.setMaxLength(50)
        self.nom_input.setPlaceholderText("Entrez le nom du magasin")
        self.auteur_input = QLineEdit()
        self.auteur_input.setPlaceholderText("Entrez le(s) gestionnaire(s)")
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        info_layout.addRow("Nom du magasin *", self.nom_input)
        info_layout.addRow("Gestionnaire(s)", self.auteur_input)
        info_layout.addRow("Date de création", self.date_input)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Fichiers
        files_group = QGroupBox("Fichiers")
        files_layout = QFormLayout()
        self.chemin_input = QLineEdit()
        self.chemin_input.setReadOnly(True)
    
        btn_browse = QPushButton("Parcourir...")
        btn_browse.clicked.connect(self.browse_file)
        file_row = QHBoxLayout()
        file_row.addWidget(self.chemin_input)
        file_row.addWidget(btn_browse)
        files_layout.addRow("Plan du magasin (image)", file_row)

        self.json_input = QLineEdit()
        self.json_input.setReadOnly(True)
        btn_json = QPushButton("Parcourir...")
        btn_json.clicked.connect(self.browse_json)
        json_row = QHBoxLayout()
        json_row.addWidget(self.json_input)
        json_row.addWidget(btn_json)
        files_layout.addRow("Articles (.json)", json_row)

        self.plan_json_input = QLineEdit()
        self.plan_json_input.setReadOnly(True)
        btn_plan_json = QPushButton("Parcourir...")
        btn_plan_json.clicked.connect(self.browse_plan_json)
        plan_row = QHBoxLayout()
        plan_row.addWidget(self.plan_json_input)
        plan_row.addWidget(btn_plan_json)
        files_layout.addRow("Quadrillage (.json)", plan_row)

        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group)

        # À propos
        apropos_group = QGroupBox("À propos du magasin")
        apropos_layout = QVBoxLayout()
        self.apropos_input = QTextEdit()
        self.apropos_input.setPlaceholderText("Décrivez votre magasin...")
        apropos_layout.addWidget(self.apropos_input)
        apropos_group.setLayout(apropos_layout)
        main_layout.addWidget(apropos_group)

        # Bouton de sauvegarde
        btn_creer = QPushButton("Sauvegarder")
        btn_creer.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn_creer.clicked.connect(self.finish)
        btn_creer.setStyleSheet("""
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
        """)
        main_layout.addWidget(btn_creer, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Données du magasin pour pré-remplir les champs
        if self.shop_data:
            self.nom_input.setText(self.shop_data.get("nom", ""))
            self.auteur_input.setText(self.shop_data.get("auteur", ""))
            date_str = self.shop_data.get("date_creation", "")
            if date_str:
                date = QDate.fromString(date_str, "dd/MM/yyyy")
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
        auteur = self.auteur_input.text()
        date = self.date_input.date().toString("dd/MM/yyyy")
        apropos = self.apropos_input.toPlainText()
        chemin = self.chemin_input.text()
        json_path = self.json_input.text()
        plan_json_path = self.plan_json_input.text()

        # Relatif à la base de données
        import sqlite3
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()

        # Vérifier si le magasin existe déjà pour cet utilisateur
        c.execute("SELECT id FROM shops WHERE user_id=?", (self.user_id,))
        row = c.fetchone()
        if row:
            # Mise à jour
            c.execute("""
                UPDATE shops SET nom=?, auteur=?, date_creation=?, apropos=?, chemin=?, articles_json=?, plan_json=?
                WHERE user_id=?
            """, (nom, auteur, date, apropos, chemin, json_path, plan_json_path, self.user_id))
        else:
            # Insertion
            c.execute("""
                INSERT INTO shops (user_id, nom, auteur, date_creation, apropos, chemin, articles_json, plan_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.user_id, nom, auteur, date, apropos, chemin, json_path, plan_json_path))
        conn.commit()
        conn.close()

        self.accept()

    def browse_file(self):
        """Ouvre un dialogue pour sélectionner une image du plan du magasin."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.bmp *.jpeg)")
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.chemin_input.setText(selected[0])

    def browse_json(self):
        """Ouvre un dialogue pour sélectionner un fichier JSON d'articles."""
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers JSON (*.json)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.json_input.setText(selected[0])

    def browse_plan_json(self):
        """Ouvre un dialogue pour sélectionner un fichier JSON de plan (quadrillage) du magasin."""
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers JSON (*.json)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.plan_json_input.setText(selected[0])