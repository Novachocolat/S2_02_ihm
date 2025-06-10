# ==============================================================
# Market Tracer - Page client
# ==============================================================
# Importations
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QListWidget,
    QLineEdit, QCheckBox, QSpinBox, QGroupBox, QGridLayout, QMenuBar, QMenu, QFileDialog, QComboBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import sys
import json

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Client")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.resize(1400, 900) 
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background: #fff;") 
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Menu déroulant
        menubar = QMenuBar()
        menubar.setStyleSheet("""
            QMenuBar { background: #f7f7fb; color: #222; font-size: 20px; font-weight: bold; }
            QMenuBar::item { background: #f7f7fb; color: #222; }
            QMenuBar::item:selected { background: #e0e0e0; }
            QMenu { background: #fff; color: #222; }
            QMenu::item:selected { background: #e0e0e0; color: #222; }
        """)

        # Fichier
        fichier_menu = menubar.addMenu("Fichier")
        fichier_menu.addAction("Ouvrir")
        fichier_menu.addAction("Charger")
        fichier_menu.addAction("Fermer")
        fichier_menu.addAction("Exporter")

        # Liste
        liste_menu = menubar.addMenu("Liste")
        liste_menu.addAction("Ajouter")
        liste_menu.addAction("Retirer")
        liste_menu.addAction("Importer")
        liste_menu.addAction("Exporter")

        # Aide
        aide_menu = menubar.addMenu("Aide")
        aide_menu.addAction("À propos")
        aide_menu.addAction("Documentation")
        aide_menu.addAction("Licence")

        # Bouton déconnexion à droite du menubar
        btn_deconnexion = QPushButton("Déconnexion")
        btn_deconnexion.setStyleSheet("background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;")
        btn_deconnexion.clicked.connect(self.deconnexion)
        menubar.setCornerWidget(btn_deconnexion, Qt.Corner.TopRightCorner)

        main_layout.addWidget(menubar)

        # Partie centrale
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)

        # Colonne gauche
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        # Produits disponibles
        prod_label = QLabel("Produits disponibles")
        prod_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        prod_label.setStyleSheet("color: #222;")
        left_col.addWidget(prod_label)

        # Saisir produit
        saisir_label = QLabel("Saisissez un produit")
        saisir_label.setFont(QFont("Arial", 10))
        saisir_label.setStyleSheet("color: #222;")
        left_col.addWidget(saisir_label)
        saisir_input = QLineEdit()
        saisir_input.setStyleSheet("color: #222; background: #fff;")
        left_col.addWidget(saisir_input)

        # Boutons stock
        btn_ajouter = QPushButton("Ajouter à mon stock")
        btn_ajouter.setStyleSheet("background: #4be39a; color: #222; font-weight: bold; min-height: 32px;")
        btn_retirer = QPushButton("Retirer de mon stock")
        btn_retirer.setStyleSheet("background: #ff3c2f; color: #222; font-weight: bold; min-height: 32px;")
        left_col.addWidget(btn_ajouter)
        left_col.addWidget(btn_retirer)

        # Filtre par catégorie
        self.filtre_combo = QComboBox()
        self.filtre_combo.setStyleSheet("background: #ededed; color: #222; font-weight: bold;")
        self.filtre_combo.addItem("Toutes les catégories")
        self.filtre_combo.currentTextChanged.connect(self.filtrer_stocks)
        left_col.addWidget(self.filtre_combo)

        # Vos stocks
        stocks_label = QLabel("Vos stocks")
        stocks_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stocks_label.setStyleSheet("color: #222;")
        left_col.addWidget(stocks_label)

        # Bouton pour choisir un fichier JSON
        btn_choisir_fichier = QPushButton("Choisir un fichier JSON")
        btn_choisir_fichier.setStyleSheet("background: #ededed; color: #222; font-weight: bold;")
        btn_choisir_fichier.clicked.connect(self.ouvrir_fichier_json)
        left_col.addWidget(btn_choisir_fichier)

        self.stocks_list = QListWidget()
        self.stocks_list.setStyleSheet("background: #ededed; color: #222; font-size: 15px;")
        left_col.addWidget(self.stocks_list)

        self.stocks_list.itemClicked.connect(self.afficher_details_produit)
        self.produit_categorie_map = {}  

        left_col.addStretch()
        left_frame = QFrame()
        left_frame.setLayout(left_col)
        left_frame.setMinimumWidth(240)
        left_frame.setMaximumWidth(320)
        left_frame.setStyleSheet("background: #f7f7fb; border-radius: 8px;")
        center_layout.addWidget(left_frame, stretch=0)

        # Colonne centrale
        plan_col = QVBoxLayout()
        plan_label = QLabel("Plan du magasin")
        plan_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        plan_label.setStyleSheet("color: #222;")
        plan_col.addWidget(plan_label)
        plan_frame = QFrame()
        plan_frame.setStyleSheet("background: #888; border-radius: 8px;")
        plan_frame.setMinimumSize(600, 400)
        plan_col.addWidget(plan_frame, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        center_layout.addWidget(plan_widget, stretch=2)

        # Colonne droite
        right_col = QVBoxLayout()
        
        # Boutons parcours
        btn_generer = QPushButton("Générer mon parcours")
        btn_generer.setStyleSheet("background: #4be39a; color: #222; font-weight: bold; min-height: 32px;")
        btn_effacer = QPushButton("Effacer mon parcours")
        btn_effacer.setStyleSheet("background: #ff3c2f; color: #222; font-weight: bold; min-height: 32px;")
        btn_exporter = QPushButton("Exporter mon parcours")
        btn_exporter.setStyleSheet("background: #aaaaaa; color: #222; font-weight: bold; min-height: 32px;")
        right_col.addWidget(btn_generer)
        right_col.addWidget(btn_effacer)
        right_col.addWidget(btn_exporter)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setStyleSheet("background: #f7f7fb; border-radius: 8px;")
        right_widget.setMinimumWidth(220)
        right_widget.setMaximumWidth(300)

        # Ajouter la colonne droite au layout central
        center_layout.addWidget(right_widget)

        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setStyleSheet("background: #ededed; color: #222; padding: 6px; border-radius: 4px;")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

    def ouvrir_fichier_json(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Fichiers JSON (*.json)")
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                self.afficher_stocks_depuis_json(filenames[0])
                self.status_bar.setText(f"Fichier chargé : {filenames[0]}")

    def afficher_stocks_depuis_json(self, chemin):
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
                for categorie, produits in data.items():
                    self.categories.add(categorie)
                    for produit in produits:
                        self.stocks_list.addItem(produit)
                        self.produit_categorie_map[produit] = categorie
            # Remplir le menu déroulant des catégories
            self.filtre_combo.blockSignals(True)
            self.filtre_combo.clear()
            self.filtre_combo.addItem("Toutes les catégories")
            for cat in sorted(self.categories):
                self.filtre_combo.addItem(cat)
            self.filtre_combo.blockSignals(False)
            self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis le fichier.")
        except Exception as e:
            self.stocks_list.addItem("Erreur de lecture du fichier")
            self.status_bar.setText("Erreur lors du chargement du fichier.")

    def afficher_details_produit(self, item):
        produit = item.text()
        categorie = self.produit_categorie_map.get(produit, "Inconnu")
        self.produit_label.setText(f"Produit : {produit}")
        self.categorie_label.setText(f"Catégorie : {categorie}")

    def filtrer_stocks(self, categorie):
        self.stocks_list.clear()
        if not hasattr(self, "produit_categorie_map"):
            return
        if categorie == "Toutes les catégories":
            for produit in self.produit_categorie_map:
                self.stocks_list.addItem(produit)
        else:
            for produit, cat in self.produit_categorie_map.items():
                if cat == categorie:
                    self.stocks_list.addItem(produit)

    def deconnexion(self):
        from main import LoginWindow  
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


# ==============================================================
# Lancement de l'application
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())