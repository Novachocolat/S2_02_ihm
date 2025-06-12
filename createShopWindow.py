from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QFrame, QFileDialog, QApplication, QDateEdit
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QDate
import sys
import sqlite3

class CreateShopWindow(QDialog): 
    def __init__(self, user_id, parent=None, shop_data=None):
        super().__init__(parent)
        self.setWindowTitle("Market Tracer - Créer un magasin")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.setMinimumSize(900, 600)
        # SUPPRIME la feuille de style globale ici pour laisser le thème du système agir
        self.user_id = user_id
        self.shop_data = shop_data
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # Partie gauche (formulaire)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.setSpacing(16)

        # Titre
        title = QLabel("Créer un magasin")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        left_layout.addWidget(title)

        # Barre horizontale sous le titre (optionnelle)
        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setFrameShadow(QFrame.Shadow.Sunken)
        hline.setLineWidth(1)
        hline.setMidLineWidth(0)
        left_layout.addWidget(hline)

        # Nom du magasin
        nom_label = QLabel("Nom du magasin")
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Entrez le nom du magasin")
        left_layout.addWidget(nom_label)
        left_layout.addWidget(self.nom_input)

        # Auteur(s)
        auteur_label = QLabel("Gestionnaire(s) du magasin")
        self.auteur_input = QLineEdit()
        self.auteur_input.setPlaceholderText("Entrez le(s) gestionnaire(s) du magasin")
        left_layout.addWidget(auteur_label)
        left_layout.addWidget(self.auteur_input)

        # Date de création
        date_label = QLabel("Date de création")
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        left_layout.addWidget(date_label)
        left_layout.addWidget(self.date_input)

        # À propos
        apropos_label = QLabel("À propos du magasin")
        self.apropos_input = QTextEdit()
        self.apropos_input.setPlaceholderText("Décrivez votre magasin...")
        left_layout.addWidget(apropos_label)
        left_layout.addWidget(self.apropos_input)

        # Chemin du plan
        chemin_label = QLabel("Chemin du Plan")
        chemin_layout = QHBoxLayout()
        self.chemin_input = QLineEdit()
        self.chemin_input.setReadOnly(True)
        btn_browse = QPushButton("Parcourir...")
        btn_browse.clicked.connect(self.browse_file)
        chemin_layout.addWidget(self.chemin_input)
        chemin_layout.addWidget(btn_browse)
        left_layout.addWidget(chemin_label)
        left_layout.addLayout(chemin_layout)

        # Chemin du fichier JSON des articles
        json_label = QLabel("Articles (.json)")
        json_layout = QHBoxLayout()
        self.json_input = QLineEdit()
        self.json_input.setReadOnly(True)
        btn_json = QPushButton("Parcourir...")
        btn_json.clicked.connect(self.browse_json)
        json_layout.addWidget(self.json_input)
        json_layout.addWidget(btn_json)
        left_layout.addWidget(json_label)
        left_layout.addLayout(json_layout)

        # Bouton Créer
        btn_creer = QPushButton("Créer / Modifier")
        btn_creer.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn_creer.clicked.connect(self.finish)
        left_layout.addSpacing(10)
        left_layout.addWidget(btn_creer, alignment=Qt.AlignmentFlag.AlignHCenter)
        btn_creer.setStyleSheet("""
                QPushButton {
                    background: #4be39a;
                    color: #fff;
                    border-radius: 6px;
                    min-width: 100px;
                    min-height: 36px;
                    font-size: 16px;
                }
                QPushButton:checked {
                    border: 2px solid #222;
                    background: #111;
                    color: #fff;
                }
            """)

        main_layout.addWidget(left_frame, stretch=3)

        # Partie droite (image ou illustration)
        right_frame = QFrame()
        right_frame.setMinimumWidth(260)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label = QLabel()
        img_label.setText("🛒")
        img_label.setFont(QFont("Arial", 80))
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(img_label)
        main_layout.addWidget(right_frame, stretch=2)

        if self.shop_data:
            self.nom_input.setText(self.shop_data.get("nom", ""))
            self.auteur_input.setText(self.shop_data.get("auteur", ""))
            self.date_input.setDate(QDate.fromString(self.shop_data.get("date_creation", ""), "dd/MM/yyyy"))
            self.apropos_input.setPlainText(self.shop_data.get("apropos", ""))
            self.chemin_input.setText(self.shop_data.get("chemin", ""))
            self.json_input.setText(self.shop_data.get("articles_json", ""))

    def finish(self):
        # Récupération des valeurs du formulaire
        nom = self.nom_input.text()
        auteur = self.auteur_input.text()
        date = self.date_input.date().toString("dd/MM/yyyy")
        apropos = self.apropos_input.toPlainText()
        chemin = self.chemin_input.text()
        json_path = self.json_input.text()

        # Lecture du contenu du fichier JSON (au lieu de stocker le chemin)
        articles_json_content = None
        if json_path:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    articles_json_content = f.read()
            except Exception:
                articles_json_content = None

        # Insertion des données du magasin (on stocke le contenu JSON, pas le chemin)
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO shops (nom, auteur, date_creation, apropos, chemin, articles_json, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nom, auteur, date, apropos, chemin, articles_json_content, self.user_id))
        conn.commit()
        conn.close()

        self.close()

    def browse_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.chemin_input.setText(selected[0])

    def browse_json(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers JSON (*.json)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.json_input.setText(selected[0])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateShopWindow(1)
    window.show()
    sys.exit(app.exec())