# ==============================================================
# Market Tracer - Page gérant
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
# ==============================================================
# Page d'administration

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Admin")
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

        # Stock
        stock_menu = menubar.addMenu("Stock")
        stock_menu.addAction("Ajouter")
        stock_menu.addAction("Retirer")
        stock_menu.addAction("Importer")

        # Gestion
        gestion_menu = menubar.addMenu("Gestion")
        gestion_menu.addAction("Modifier mon magasin")
        gestion_menu.addAction("Créer un employé")
        gestion_menu.addAction("Modifier un employé")
        gestion_menu.addAction("Supprimer un employé")

        # Plan
        plan_menu = menubar.addMenu("Plan")
        plan_menu.addAction("Ouvrir")
        plan_menu.addAction("Afficher")
        plan_menu.addAction("Paramétrer")

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
        right_col.setSpacing(18)  

        # Plan
        plan_box = QGroupBox("Plan")
        plan_box.setMinimumWidth(220)
        plan_box.setStyleSheet("QGroupBox { background: #fff; border-radius: 6px; font-weight: bold; color: #222; }")
        plan_box_layout = QVBoxLayout()
        plan_box_layout.setContentsMargins(10, 10, 10, 10)  
        plan_file_input = QLineEdit("Choisissez un fichier")
        plan_file_input.setStyleSheet("color: #222; background: #fff;")
        plan_box_layout.addWidget(plan_file_input)
        plan_box.setLayout(plan_box_layout)
        right_col.addWidget(plan_box)

        # Espacement entre les blocs
        right_col.addSpacing(10)

        # Quadrillage
        grid_box = QGroupBox("Quadrillage")
        grid_box.setMinimumWidth(220)
        grid_box.setStyleSheet("QGroupBox { background: #fff; border-radius: 6px; font-weight: bold; color: #222; }")
        grid_layout = QVBoxLayout()
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_checkbox = QCheckBox("Afficher le quadrillage")
        grid_checkbox.setStyleSheet("color: #222;")
        grid_layout.addWidget(grid_checkbox)
        grid_pos_label = QLabel("Position du quadrillage")
        grid_pos_label.setStyleSheet("color: #222;")
        grid_layout.addWidget(grid_pos_label)
        pos_layout = QHBoxLayout()
        x_label = QLabel("x :")
        x_label.setStyleSheet("color: #222;")
        pos_layout.addWidget(x_label)
        x_spin = QSpinBox()
        x_spin.setStyleSheet("color: #222; background: #fff;")
        pos_layout.addWidget(x_spin)
        y_label = QLabel("y :")
        y_label.setStyleSheet("color: #222;")
        pos_layout.addWidget(y_label)
        y_spin = QSpinBox()
        y_spin.setStyleSheet("color: #222; background: #fff;")
        pos_layout.addWidget(y_spin)
        grid_layout.addLayout(pos_layout)
        taille_label = QLabel("Taille des cases")
        taille_label.setStyleSheet("color: #222;")
        grid_layout.addWidget(taille_label)
        taille_spin = QSpinBox()
        taille_spin.setStyleSheet("color: #222; background: #fff;")
        grid_layout.addWidget(taille_spin)
        grid_box.setLayout(grid_layout)
        right_col.addWidget(grid_box)

        right_col.addSpacing(10)

        # Détails
        details_box = QGroupBox("Détails")
        details_box.setMinimumWidth(220)
        details_box.setStyleSheet("QGroupBox { background: #fff; border-radius: 6px; font-weight: bold; color: #222; }")
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(10, 10, 10, 10)
        produit_label = QLabel("Produit : ...")
        produit_label.setStyleSheet("color: #222; background: #f7f7fb; border-radius: 8px; padding: 2px 8px;")
        details_layout.addWidget(produit_label)
        categorie_label = QLabel("Catégorie : ...")
        categorie_label.setStyleSheet("color: #222; background: #f7f7fb; border-radius: 8px; padding: 2px 8px;")
        details_layout.addWidget(categorie_label)
        self.produit_label = produit_label
        self.categorie_label = categorie_label
        details_box.setLayout(details_layout)
        right_col.addWidget(details_box)

        right_col.addStretch()
        right_frame = QFrame()
        right_frame.setLayout(right_col)
        right_frame.setMinimumWidth(260)
        right_frame.setMaximumWidth(340)
        right_frame.setStyleSheet("background: #f7f7fb; border-radius: 8px;")
        center_layout.addWidget(right_frame, stretch=0)

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