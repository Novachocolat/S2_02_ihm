# ==============================================================
# Vue pour la fenêtre d'administration du gérant
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLineEdit, QGroupBox, QMenuBar, QComboBox, QMessageBox, QSlider
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from grid import GridOverlay, DraggableListWidget

class AdminView(QWidget):
    """Vue pour la fenêtre d'administration du gérant"""
    def __init__(self):
        """Initialise la vue d'administration du gérant."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Gérant")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setMinimumSize(1280, 768)
        self.categories = set() # Ensemble pour stocker les catégories de produits
        self.produit_categorie_map = {} # Dictionnaire pour stocker les produits et leurs catégories
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre d'administration."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Barre de menu
        self.menubar = QMenuBar()
        self.fichier_menu = self.menubar.addMenu("Fichier")
        self.action_charger = self.fichier_menu.addAction("Charger")

        self.gestion_menu = self.menubar.addMenu("Gestion")
        self.action_configurer = self.gestion_menu.addAction("Configurer mon magasin")
        self.action_gestion_employes = self.gestion_menu.addAction("Gérer les employés")

        self.plan_menu = self.menubar.addMenu("Plan")
        self.action_ouvrir_plan = self.plan_menu.addAction("Ouvrir un plan")
        self.action_reinitialiser_plan = self.plan_menu.addAction("Réinitialiser le plan")
        self.action_exporter_json = self.plan_menu.addAction("Exporter en JSON")
        self.action_importer_json = self.plan_menu.addAction("Importer depuis JSON")

        self.aide_menu = self.menubar.addMenu("Aide")
        self.action_about = self.aide_menu.addAction("À propos")
        self.action_doc = self.aide_menu.addAction("Notice d'utilisation")
        self.action_licence = self.aide_menu.addAction("Licence")

        # Déconnexion
        self.btn_deconnexion = QPushButton("Déconnexion")
        self.btn_deconnexion.setStyleSheet("background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;")
        self.menubar.setCornerWidget(self.btn_deconnexion, Qt.Corner.TopRightCorner)
        main_layout.addWidget(self.menubar)

        # Ligne horizontale sous la barre de menu
        hline_menu = QFrame()
        hline_menu.setFrameShape(QFrame.Shape.HLine)
        hline_menu.setFrameShadow(QFrame.Shadow.Sunken)
        hline_menu.setLineWidth(1)
        hline_menu.setMidLineWidth(0)
        main_layout.addWidget(hline_menu)

        # Partie centrale
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)

        # Colonne gauche
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        gestion_frame = QFrame()
        gestion_layout = QVBoxLayout(gestion_frame)
        gestion_layout.setContentsMargins(8, 8, 8, 8)
        gestion_layout.setSpacing(6)
        gestion_label = QLabel("Gestion des stocks")
        gestion_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        gestion_layout.addWidget(gestion_label)

        # Ajouter au stock
        self.btn_ajouter = QPushButton("Ajouter à mon stock")
        self.btn_ajouter.setFixedHeight(28)
        self.btn_ajouter.setStyleSheet("background: #56E39F; ")
        gestion_layout.addWidget(self.btn_ajouter)

        # Retirer du stock
        self.btn_retirer = QPushButton("Retirer de mon stock")
        self.btn_retirer.setFixedHeight(28)
        self.btn_retirer.setStyleSheet("background: #FF6B3D; ")
        gestion_layout.addWidget(self.btn_retirer)
        left_col.addWidget(gestion_frame)

        # Filtrer par catégorie
        filtre_label = QLabel("Filtre")
        filtre_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(filtre_label)
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem("Toutes les catégories")
        left_col.addWidget(self.filtre_combo)

        # Recercher un article
        search_label = QLabel("Rechercher")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        left_col.addWidget(self.search_input)

        # Stocks
        stocks_label = QLabel("Vos stocks")
        stocks_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_col.addWidget(stocks_label)
        self.stocks_list = DraggableListWidget()
        self.stocks_list.setDragEnabled(True)
        left_col.addWidget(self.stocks_list, stretch=1)

        left_col.addStretch()
        left_frame = QFrame()
        left_frame.setLayout(left_col)
        left_frame.setMinimumWidth(240)
        left_frame.setMaximumWidth(320)
        center_layout.addWidget(left_frame, stretch=0)

        # Séparateur vertical
        vline1 = QFrame()
        vline1.setFrameShape(QFrame.Shape.VLine)
        vline1.setFrameShadow(QFrame.Shadow.Sunken)
        vline1.setLineWidth(1)
        vline1.setMidLineWidth(0)
        center_layout.addWidget(vline1)

        # Colonne centrale
        plan_col = QVBoxLayout()
        plan_label = QLabel("Plan du magasin")
        plan_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        plan_col.addWidget(plan_label)
        self.grid_overlay = GridOverlay()
        plan_col.addWidget(self.grid_overlay, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        center_layout.addWidget(plan_widget, stretch=2)

        # Séparateur vertical
        vline2 = QFrame()
        vline2.setFrameShape(QFrame.Shape.VLine)
        vline2.setFrameShadow(QFrame.Shadow.Sunken)
        vline2.setLineWidth(1)
        vline2.setMidLineWidth(0)
        center_layout.addWidget(vline2)

        # Colonne droite
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        comm_box = QGroupBox("Commandes")
        comm_box.setMinimumWidth(220)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_ouvrir_image = QPushButton("Ouvrir un plan")
        self.btn_ouvrir_image.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_ouvrir_image)
        self.btn_reinitialiser = QPushButton("Réinitialiser")
        self.btn_reinitialiser.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_reinitialiser)
        self.btn_exporter = QPushButton("Exporter en JSON")
        self.btn_exporter.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_exporter)
        self.btn_importer = QPushButton("Importer en JSON")
        self.btn_importer.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_importer)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        outils_box = QGroupBox("Outils")
        outils_box.setMinimumWidth(220)
        outils_layout = QVBoxLayout()
        outils_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_deplacer = QPushButton("Se déplacer")
        self.btn_deplacer.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_deplacer)
        self.btn_rayon = QPushButton("Rayon")
        self.btn_rayon.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_rayon)
        self.btn_stock = QPushButton("Stock")
        self.btn_stock.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_stock)
        self.btn_caisse = QPushButton("Caisse")
        self.btn_caisse.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_caisse)
        self.btn_entree = QPushButton("Entrée")
        self.btn_entree.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_entree)
        self.btn_sortie = QPushButton("Sortie")
        self.btn_sortie.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_sortie)
        self.btn_supprimer = QPushButton("Effacer")
        self.btn_supprimer.setMinimumHeight(25)
        outils_layout.addWidget(self.btn_supprimer)
        outils_box.setLayout(outils_layout)
        right_col.addWidget(outils_box)

        # Zoom et grille
        zoom_box = QGroupBox("Zoom")
        zoom_box.setMinimumWidth(220)
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(10, 10, 10, 10)

        label_grid_size = QLabel("Grille :\nAjuste la taille des cases sur le quadrillage")
        label_grid_size.setWordWrap(True)
        zoom_layout.addWidget(label_grid_size)
        self.slider_grid = QSlider(Qt.Orientation.Horizontal)
        self.slider_grid.setMinimum(25)
        self.slider_grid.setMaximum(100)
        self.slider_grid.setValue(50)
        zoom_layout.addWidget(self.slider_grid)

        label_zoom = QLabel("Zoom :\nAgrandit ou réduit le plan")
        label_zoom.setWordWrap(True)
        zoom_layout.addWidget(label_zoom)
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(10)
        self.slider_zoom.setMaximum(300)
        self.slider_zoom.setValue(50)
        self.grid_overlay.set_zoom(self.slider_zoom.value() / 100.0)
        zoom_layout.addWidget(self.slider_zoom)

        zoom_box.setLayout(zoom_layout)
        right_col.addWidget(zoom_box)

        right_col.addStretch()
        right_frame = QFrame()
        right_frame.setLayout(right_col)
        right_frame.setMinimumWidth(240)
        right_frame.setMaximumWidth(320)
        center_layout.addWidget(right_frame, stretch=0)

        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

    def afficher_stocks_depuis_json(self, articles_json_content):
        """Affiche les stocks à partir d'un contenu JSON."""
        import json
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            data = json.loads(articles_json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    key = f"{categorie.lower()}::{produit.lower()}"
                    self.stocks_list.addItem(produit)
                    self.produit_categorie_map[key] = (categorie, produit)
            if hasattr(self, "maj_filtre_categories"):
                self.maj_filtre_categories()
            if hasattr(self, "status_bar"):
                self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis la base de données.")
        except Exception as e:
            self.stocks_list.addItem("Aucun stock trouvé.")
            if hasattr(self, "status_bar"):
                self.status_bar.setText("Erreur lors du chargement des articles.")

    def maj_filtre_categories(self):
        """Met à jour la liste des catégories dans le filtre."""
        self.filtre_combo.blockSignals(True)
        self.filtre_combo.clear()
        self.filtre_combo.addItem("Toutes les catégories")
        for cat in sorted(self.categories, key=lambda x: x.lower()):
            self.filtre_combo.addItem(cat)
        self.filtre_combo.blockSignals(False)

    def filtrer_stocks(self, categorie):
        """Filtre les stocks affichés en fonction de la catégorie sélectionnée."""
        self.stocks_list.clear()
        texte = self.search_input.text().lower() if hasattr(self, "search_input") else ""
        for key, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat.lower() == categorie.lower()) and texte in nom.lower():
                self.stocks_list.addItem(nom)

    def rechercher_stocks(self, texte):
        """Recherche des stocks en fonction du texte entré dans le champ de recherche."""
        texte = texte.lower()
        categorie = self.filtre_combo.currentText()
        self.stocks_list.clear()
        for key, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in nom.lower():
                self.stocks_list.addItem(nom)

    def retirer_article_selectionne(self):
        """Retire l'article sélectionné de la liste des stocks."""
        item = self.stocks_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return
        nom = item.text()
        key_to_remove = None
        for key, (cat, nom_map) in self.produit_categorie_map.items():
            if nom_map == nom:
                key_to_remove = key
                break
        if key_to_remove:
            del self.produit_categorie_map[key_to_remove]
            self.stocks_list.takeItem(self.stocks_list.row(item))
            self.sauvegarder_articles_json()
            self.status_bar.setText(f"Article '{nom}' retiré du stock.")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de retrouver la catégorie de l'article à retirer.")

    def sauvegarder_articles_json(self):
        """Sauvegarde les articles dans un fichier JSON."""
        import json
        data = {}
        for key, (cat, nom) in self.produit_categorie_map.items():
            data.setdefault(cat, []).append(nom)
        articles_json_content = json.dumps(data, ensure_ascii=False, indent=2)