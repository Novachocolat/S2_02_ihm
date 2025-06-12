# ==============================================================

# Market Tracer - Page client

# Développé par Noé Colin
# Dernière modification : 11/06/2025

# ==============================================================

# Importations des modules nécessaires
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QListWidget,
    QLineEdit, QMenuBar, QFileDialog, QComboBox, QGroupBox
)
from PyQt6.QtGui import QFont, QIcon, QGuiApplication
from PyQt6.QtCore import Qt
import sys
import json

# =============================================================

# Fenêtre Client

# =============================================================
class CustomerWindow(QWidget):
    def __init__(self, articles_json=None):
        super().__init__()
        print("[CustomerWindow] Initialisation de la fenêtre client")
        self.setWindowTitle("Market Tracer - Client")
        self.setWindowIcon(QIcon("img/chariot.png"))

        # Taille dynamique
        screen = QGuiApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.9), int(screen.height() * 0.9))
        self.setMinimumSize(int(screen.width() * 0.7), int(screen.height() * 0.7))
        self.showMaximized()

        print("[CustomerWindow] Connexion d'un client")
        self.articles_json = articles_json
        self.setup_ui()

    def setup_ui(self):
        print("[CustomerWindow] Construction de l'UI")
        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Barre de menus en haut
        menubar = QMenuBar()
        print("[CustomerWindow] Ajout de la barre de menus")

        # Menus principaux
        fichier_menu = menubar.addMenu("Fichier")
        fichier_menu.addAction("Ouvrir")
        fichier_menu.addAction("Charger")
        fichier_menu.addAction("Fermer")
        fichier_menu.addAction("Exporter")

        liste_menu = menubar.addMenu("Liste")
        liste_menu.addAction("Ajouter")
        liste_menu.addAction("Retirer")
        liste_menu.addAction("Importer")
        liste_menu.addAction("Exporter")

        aide_menu = menubar.addMenu("Aide")
        action_about = aide_menu.addAction("À propos")
        action_doc = aide_menu.addAction("Documentation")
        action_licence = aide_menu.addAction("Licence")

        # Connexion des actions du menu Aide
        action_about.triggered.connect(self.open_about)
        action_doc.triggered.connect(self.open_doc)
        action_licence.triggered.connect(self.open_licence)

        # Bouton déconnexion
        btn_deconnexion = QPushButton("Déconnexion")
        btn_deconnexion.setStyleSheet("background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;")
        btn_deconnexion.clicked.connect(self.deconnexion)
        menubar.setCornerWidget(btn_deconnexion, Qt.Corner.TopRightCorner)

        main_layout.addWidget(menubar)
        print("[CustomerWindow] Barre de menus ajoutée")

        # Ligne horizontale
        hline_menu = QFrame()
        hline_menu.setFrameShape(QFrame.Shape.HLine)
        hline_menu.setFrameShadow(QFrame.Shadow.Sunken)
        hline_menu.setLineWidth(1)
        hline_menu.setMidLineWidth(0)
        main_layout.addWidget(hline_menu)

        # Layout horizontal
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)

        # Colonne gauche
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        prod_label = QLabel("Produits")
        prod_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_col.addWidget(prod_label)

        saisir_label = QLabel("Recherchez un produit")
        saisir_label.setFont(QFont("Arial", 10))
        left_col.addWidget(saisir_label)
        saisir_input = QLineEdit()
        left_col.addWidget(saisir_input)

        btn_ajouter = QPushButton("Ajouter à ma liste")
        btn_ajouter.setMinimumHeight(32)
        btn_ajouter.setStyleSheet("background: #56E39F; ")
        
        btn_retirer = QPushButton("Retirer de ma liste")
        btn_retirer.setMinimumHeight(32)
        btn_retirer.setStyleSheet("background: #FF6B3D; ")
        
        left_col.addWidget(btn_ajouter)
        left_col.addWidget(btn_retirer)

        # Filtre par catégorie
        filtre_label = QLabel("Filtre")
        filtre_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_col.addWidget(filtre_label)
        
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem("Toutes les catégories")
        self.filtre_combo.currentTextChanged.connect(self.filtrer_stocks)
        left_col.addWidget(self.filtre_combo)

        # Liste des produits sélectionnés
        stocks_label = QLabel("Votre liste")
        stocks_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_col.addWidget(stocks_label)

        self.stocks_list = QListWidget()
        left_col.addWidget(self.stocks_list, stretch=1)

        self.stocks_list.itemClicked.connect(self.afficher_details_produit)
        self.produit_categorie_map = {}

        left_col.addStretch()
        left_frame = QFrame()
        left_frame.setLayout(left_col)
        left_frame.setMinimumWidth(240)
        left_frame.setMaximumWidth(320)
        center_layout.addWidget(left_frame, stretch=0)

        # Barre verticale gauche
        vline1 = QFrame()
        vline1.setFrameShape(QFrame.Shape.VLine)
        vline1.setFrameShadow(QFrame.Shadow.Sunken)
        vline1.setLineWidth(1)
        vline1.setMidLineWidth(0)
        center_layout.addWidget(vline1)

        # Plan du magasin
        plan_col = QVBoxLayout()
        plan_label = QLabel("Plan du magasin")
        plan_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        plan_col.addWidget(plan_label)
        plan_frame = QFrame()
        plan_frame.setMinimumSize(600, 400)
        plan_col.addWidget(plan_frame, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        center_layout.addWidget(plan_widget, stretch=2)

        # Barre verticale droite
        vline2 = QFrame()
        vline2.setFrameShape(QFrame.Shape.VLine)
        vline2.setFrameShadow(QFrame.Shadow.Sunken)
        vline2.setLineWidth(1)
        vline2.setMidLineWidth(0)
        center_layout.addWidget(vline2)

        # Colonne droite
        right_col = QVBoxLayout()
        right_col.setSpacing(15)

        btn_generer = QPushButton("Générer mon parcours")
        btn_generer.setMinimumHeight(32)
        btn_generer.setStyleSheet("background-color: #56E39F;")
        btn_effacer = QPushButton("Effacer mon parcours")
        btn_effacer.setMinimumHeight(32)
        btn_effacer.setStyleSheet("background: #FF6B3D; ")
        btn_exporter = QPushButton("Exporter mon parcours")
        btn_exporter.setMinimumHeight(32)
    

        # Ajoute les boutons sans espace entre eux
        right_col.addWidget(btn_generer)
        right_col.addWidget(btn_effacer)
        right_col.addWidget(btn_exporter)
        right_col.addSpacing(400)

        # Ajout du cadre de détails du produit en bas de la colonne droite
        details_box = QGroupBox("Détail")
        details_box.setMinimumWidth(220)
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(10, 10, 10, 10)
        self.produit_label = QLabel("Produit : ...")
        details_layout.addWidget(self.produit_label)
        self.categorie_label = QLabel("Catégorie : ...")
        details_layout.addWidget(self.categorie_label)
        details_box.setLayout(details_layout)
        right_col.addWidget(details_box)

        right_col.addStretch()

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setMinimumWidth(220)
        right_widget.setMaximumWidth(300)
        center_layout.addWidget(right_widget)

        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

        # À la fin de setup_ui, charge les articles si fournis
        if self.articles_json:
            print("[CustomerWindow] Chargement des articles depuis le magasin")
            try:
                data = json.loads(self.articles_json)
                self.stocks_list.clear()
                self.produit_categorie_map = {}
                self.categories = set()
                for categorie, produits in data.items():
                    print(f"[CustomerWindow] Catégorie chargée : {categorie} ({len(produits)} produits)")
                    self.categories.add(categorie)
                    for produit in produits:
                        print(f"[CustomerWindow] Produit ajouté : {produit}")
                        self.stocks_list.addItem(produit)
                        self.produit_categorie_map[produit] = categorie
                self.filtre_combo.blockSignals(True)
                self.filtre_combo.clear()
                self.filtre_combo.addItem("Toutes les catégories")
                for cat in sorted(self.categories):
                    self.filtre_combo.addItem(cat)
                self.filtre_combo.blockSignals(False)
                self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis le magasin.")
                print("[CustomerWindow] Chargement des articles terminé")
            except Exception as e:
                print(f"[CustomerWindow] Erreur lors du chargement des articles : {e}")
                self.status_bar.setText("Erreur lors du chargement des articles du magasin.")

    # Ouvre un fichier JSON et charge les produits
    def ouvrir_fichier_json(self):
        print("[CustomerWindow] Ouverture d'un fichier JSON")
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Fichiers JSON (*.json)")
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                print(f"[CustomerWindow] Fichier sélectionné : {filenames[0]}")
                self.afficher_stocks_depuis_json(filenames[0])
                self.status_bar.setText(f"Fichier chargé : {filenames[0]}")

    # Affiche les produits du fichier JSON dans la liste
    def afficher_stocks_depuis_json(self, chemin):
        print(f"[CustomerWindow] Chargement des produits depuis le fichier : {chemin}")
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
                for categorie, produits in data.items():
                    print(f"[CustomerWindow] Catégorie chargée : {categorie} ({len(produits)} produits)")
                    self.categories.add(categorie)
                    for produit in produits:
                        print(f"[CustomerWindow] Produit ajouté : {produit}")
                        self.stocks_list.addItem(produit)
                        self.produit_categorie_map[produit] = categorie
            self.filtre_combo.blockSignals(True)
            self.filtre_combo.clear()
            self.filtre_combo.addItem("Toutes les catégories")
            for cat in sorted(self.categories):
                self.filtre_combo.addItem(cat)
            self.filtre_combo.blockSignals(False)
            self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis le fichier.")
            print("[CustomerWindow] Chargement depuis fichier terminé")
        except Exception as e:
            print(f"[CustomerWindow] Erreur de lecture du fichier : {e}")
            self.stocks_list.addItem("Erreur de lecture du fichier")
            self.status_bar.setText("Erreur lors du chargement du fichier.")

    # Affiche les détails du produit sélectionné
    def afficher_details_produit(self, item):
        produit = item.text()
        categorie = self.produit_categorie_map.get(produit, "Inconnu")
        print(f"[CustomerWindow] Détail produit sélectionné : {produit} (Catégorie : {categorie})")
        self.produit_label.setText(f"Produit : {produit}")
        self.categorie_label.setText(f"Catégorie : {categorie}")

    # Filtre la liste des produits selon la catégorie sélectionnée
    def filtrer_stocks(self, categorie):
        print(f"[CustomerWindow] Filtrage des stocks sur la catégorie : {categorie}")
        self.stocks_list.clear()
        if not hasattr(self, "produit_categorie_map"):
            print("[CustomerWindow] Aucun mapping produit-catégorie")
            return
        if categorie == "Toutes les catégories":
            for produit in self.produit_categorie_map:
                self.stocks_list.addItem(produit)
        else:
            for produit, cat in self.produit_categorie_map.items():
                if cat == categorie:
                    self.stocks_list.addItem(produit)

    # Déconnecte l'utilisateur et retourne à la fenêtre de connexion
    def deconnexion(self):
        print("[CustomerWindow] Déconnexion demandée")
        from main import LoginWindow
        self.close()
        print("[CustomerWindow] Déconnexion d'un client")
        self.login_window = LoginWindow()
        self.login_window.show()

    # Ouvre la fenêtre "À propos"
    def open_about(self):
        from aboutWindow import AboutWindow
        self.about_window = AboutWindow()
        self.about_window.show()

    # Ouvre la fenêtre "Documentation"
    def open_doc(self):
        from docWindow import DocWindow
        self.doc_window = DocWindow()
        self.doc_window.show()

    # Ouvre la fenêtre "Licence"
    def open_licence(self):
        from licenceWindow import LicenceWindow
        self.licence_window = LicenceWindow()
        self.licence_window.show()
# ==============================================================
# Lancement de l'application
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomerWindow()
    window.show()
    sys.exit(app.exec())