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
        self.setStyleSheet("background: #f7f7fb;")
        self.user_id = user_id
        self.shop_data = shop_data
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Partie gauche (formulaire)
        left_frame = QFrame()
        left_frame.setStyleSheet("background: #f7f7fb;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.setSpacing(18)

        # Titre
        title = QLabel("Créer un magasin")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 20px;")
        left_layout.addWidget(title)

        # Nom du projet
        nom_label = QLabel("Nom du magasin")
        nom_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        nom_label.setStyleSheet("color: #222;")
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Entrez le nom du magasin")
        self.nom_input.setStyleSheet("background: #888; color: #fff; border-radius: 4px; padding: 6px;")
        left_layout.addWidget(nom_label)
        left_layout.addWidget(self.nom_input)

        # Auteur(s)
        auteur_label = QLabel("Gestionnaire(s) du magasin")
        auteur_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        auteur_label.setStyleSheet("color: #222;")
        self.auteur_input = QLineEdit()
        self.auteur_input.setPlaceholderText("Entrez le(s) gestionnaire(s) du magasin")
        self.auteur_input.setStyleSheet("background: #888; color: #fff; border-radius: 4px; padding: 6px;")
        left_layout.addWidget(auteur_label)
        left_layout.addWidget(self.auteur_input)

        # Date de création
        date_label = QLabel("Date de création")
        date_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        date_label.setStyleSheet("color: #222;")
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet("background: #fff; color: #222; border-radius: 4px; padding: 6px;")
        left_layout.addWidget(date_label)
        left_layout.addWidget(self.date_input)

        # À propos
        apropos_label = QLabel("À PROPOS DE CE MAGASIN")
        apropos_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        apropos_label.setStyleSheet("color: #222;")
        self.apropos_input = QTextEdit()
        self.apropos_input.setStyleSheet("background: #888; color: #fff; border-radius: 6px; padding: 6px; min-height: 100px;")
        left_layout.addWidget(apropos_label)
        left_layout.addWidget(self.apropos_input)

        # Chemin du plan
        chemin_label = QLabel("Chemin du Plan")
        chemin_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        chemin_label.setStyleSheet("color: #222;")
        chemin_layout = QHBoxLayout()
        self.chemin_input = QLineEdit()
        self.chemin_input.setReadOnly(True)
        self.chemin_input.setStyleSheet("background: #fff; color: #222; border-radius: 4px; padding: 6px;")
        btn_browse = QPushButton("Parcourir...")
        btn_browse.setStyleSheet("background: #bdbdbd; color: #222; border-radius: 4px; padding: 6px;")
        btn_browse.clicked.connect(self.browse_file)
        chemin_layout.addWidget(self.chemin_input)
        chemin_layout.addWidget(btn_browse)
        left_layout.addWidget(chemin_label)
        left_layout.addLayout(chemin_layout)

        # Ajout du chemin du fichier JSON des articles
        json_label = QLabel("Articles (.json)")
        json_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        json_label.setStyleSheet("color: #222;")
        json_layout = QHBoxLayout()
        self.json_input = QLineEdit()
        self.json_input.setReadOnly(True)
        self.json_input.setStyleSheet("background: #fff; color: #222; border-radius: 4px; padding: 6px;")
        btn_json = QPushButton("Parcourir...")
        btn_json.setStyleSheet("background: #bdbdbd; color: #222; border-radius: 4px; padding: 6px;")
        btn_json.clicked.connect(self.browse_json)
        json_layout.addWidget(self.json_input)
        json_layout.addWidget(btn_json)
        left_layout.addWidget(json_label)
        left_layout.addLayout(json_layout)

        # Bouton Créer
        btn_creer = QPushButton("Créer")
        btn_creer.setStyleSheet("""
            QPushButton {
                background: #bdbdbd;
                color: #222;
                border-radius: 6px;
                min-height: 36px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background: #888;
            }
        """)
        btn_creer.clicked.connect(self.finish)
        left_layout.addSpacing(10)
        left_layout.addWidget(btn_creer, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addWidget(left_frame, stretch=3)

        # Partie droite (image)
        right_frame = QFrame()
        right_frame.setStyleSheet("background: #888;")
        right_frame.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label = QLabel("IMAGE")
        img_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        img_label.setStyleSheet("color: #fff;")
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

        # Création de la base de données et de la table si besoin
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                auteur TEXT,
                date_creation TEXT,
                apropos TEXT,
                chemin TEXT,
                articles_json TEXT,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        # S'assure que la colonne articles_json existe
        try:
            c.execute("ALTER TABLE shops ADD COLUMN articles_json TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            c.execute("ALTER TABLE shops ADD COLUMN user_id INTEGER")
        except sqlite3.OperationalError:
            pass

        # Insertion des données du magasin
        c.execute("""
            INSERT INTO shops (nom, auteur, date_creation, apropos, chemin, articles_json, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nom, auteur, date, apropos, chemin, json_path, self.user_id))
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
    window = CreateShopWindow(1)  # user_id fictif pour le test
    window.show()
    sys.exit(app.exec())