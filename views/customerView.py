# ==============================================================
# Vue pour la fenêtre client & employé
# Développé par N. COLIN, D. MELOCCO
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLineEdit, QGroupBox, QMenuBar, QComboBox, QSlider
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from grid import GridOverlay, DraggableListWidget

class CustomerView(QWidget):
    """Vue pour la fenêtre client"""
    def __init__(self):
        """Initialise la vue client."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Client & Employé")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setMinimumSize(1280, 768)
        self.categories = set() # Ensemble pour stocker les catégories de produits
        self.produit_categorie_map = {} # Dictionnaire pour stocker les produits et leurs catégories
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre client."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Barre de menu
        self.menubar = QMenuBar()
        self.fichier_menu = self.menubar.addMenu("Fichier")
        self.action_exporter = self.fichier_menu.addAction("Exporter ma liste")
        self.action_importer = self.fichier_menu.addAction("Importer une liste")

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

        # Colonne gauche : gestion de la liste de courses
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        liste_frame = QFrame()
        liste_layout = QVBoxLayout(liste_frame)
        liste_layout.setContentsMargins(8, 8, 8, 8)
        liste_layout.setSpacing(6)
        liste_label = QLabel("Liste de courses")
        liste_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        liste_layout.addWidget(liste_label)
        
        # Ajouter à la liste
        self.btn_ajouter = QPushButton("Ajouter à ma liste")
        self.btn_ajouter.setFixedHeight(28)
        self.btn_ajouter.setStyleSheet("background: #56E39F; ")
        liste_layout.addWidget(self.btn_ajouter)

        # Retirer de la liste
        self.btn_retirer = QPushButton("Retirer de ma liste")
        self.btn_retirer.setFixedHeight(28)
        self.btn_retirer.setStyleSheet("background: #FF6B3D; ")
        liste_layout.addWidget(self.btn_retirer)

        # Filtrer par catégorie
        filtre_label = QLabel("Filtre")
        filtre_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        liste_layout.addWidget(filtre_label)
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem("Toutes les catégories")
        liste_layout.addWidget(self.filtre_combo)

        # Recherche d'article
        search_label = QLabel("Rechercher")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        liste_layout.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        liste_layout.addWidget(self.search_input)

        # Liste des produits disponibles
        produits_label = QLabel("Articles disponibles")
        produits_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        liste_layout.addWidget(produits_label)
        self.stocks_list = DraggableListWidget()
        self.stocks_list.setDragEnabled(False)
        liste_layout.addWidget(self.stocks_list, stretch=1)

        # Liste de courses du client
        liste_courses_label = QLabel("Votre liste de courses")
        liste_courses_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        liste_layout.addWidget(liste_courses_label)
        self.courses_list = DraggableListWidget()
        self.courses_list.setDragEnabled(True)
        liste_layout.addWidget(self.courses_list, stretch=1)

        left_col.addWidget(liste_frame)
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

        # Colonne centrale : plan du magasin
        plan_col = QVBoxLayout()
        plan_label = QLabel("Plan du magasin")
        plan_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        plan_col.addWidget(plan_label)
        self.grid_overlay = GridOverlay()
        self.grid_overlay.set_pan_mode(True)
        self.grid_overlay.setInteractive(False)
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

        # Colonne droite : commandes et parcours
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        comm_box = QGroupBox("Commandes")
        comm_box.setMinimumWidth(220)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_vider_liste = QPushButton("Vider ma liste")
        self.btn_vider_liste.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_vider_liste)
        self.btn_exporter = QPushButton("Exporter ma liste")
        self.btn_exporter.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_exporter)
        self.btn_importer = QPushButton("Importer une liste")
        self.btn_importer.setMinimumHeight(25)
        comm_layout.addWidget(self.btn_importer)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        parcours_box = QGroupBox("Parcours")
        parcours_box.setMinimumWidth(220)
        parcours_layout = QVBoxLayout()
        parcours_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_generer = QPushButton("Générer le parcours")
        self.btn_generer.setMinimumHeight(25)
        parcours_layout.addWidget(self.btn_generer)
        parcours_box.setLayout(parcours_layout)
        right_col.addWidget(parcours_box)

        # Zoom
        zoom_box = QGroupBox("Zoom")
        zoom_box.setMinimumWidth(220)
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(10, 10, 10, 10)
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

    def afficher_produits_depuis_json(self, produits_json_content):
        """Affiche les produits à partir d'un contenu JSON."""
        import json
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            data = json.loads(produits_json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    key = f"{categorie.lower()}::{produit.lower()}"
                    self.stocks_list.addItem(produit)
                    self.produit_categorie_map[key] = (categorie, produit)
            self.maj_filtre_categories()
            self.status_bar.setText(f"{self.stocks_list.count()} produits chargés.")
        except Exception as e:
            self.stocks_list.addItem("Aucun produit trouvé.")
            self.status_bar.setText("Erreur lors du chargement des produits.")

    def maj_filtre_categories(self):
        """Met à jour la liste des catégories dans le filtre."""
        self.filtre_combo.blockSignals(True)
        self.filtre_combo.clear()
        self.filtre_combo.addItem("Toutes les catégories")
        for cat in sorted(self.categories, key=lambda x: x.lower()):
            self.filtre_combo.addItem(cat)
        self.filtre_combo.blockSignals(False)

    def filtrer_produits(self, categorie):
        """Filtre les produits affichés en fonction de la catégorie sélectionnée."""
        self.stocks_list.clear()
        texte = self.search_input.text().lower()
        for key, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat.lower() == categorie.lower()) and texte in nom.lower():
                self.stocks_list.addItem(nom)

    def rechercher_produits(self, texte):
        """Recherche des produits en fonction du texte entré dans le champ de recherche."""
        texte = texte.lower()
        categorie = self.filtre_combo.currentText()
        self.stocks_list.clear()
        for key, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in nom.lower():
                self.stocks_list.addItem(nom)