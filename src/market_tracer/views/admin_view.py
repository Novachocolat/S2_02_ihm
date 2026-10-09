# ==============================================================
# Vue pour la fenêtre d'administration du gérant
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMenuBar,
    QPushButton, QVBoxLayout, QWidget
)

from market_tracer.ui_helpers import (
    app_icon, bold_label, command_button, logout_button, separator,
    wrap_in_side_frame, zoom_group_box
)
from market_tracer.constants import ALL_CATEGORIES
from market_tracer.views.catalog_mixin import ProductCatalogMixin
from market_tracer.widgets.draggable_list import DraggableListWidget
from market_tracer.widgets.grid_overlay import GridOverlay


class AdminView(ProductCatalogMixin, QWidget):
    """Vue pour la fenêtre d'administration du gérant"""
    def __init__(self):
        """Initialise la vue d'administration du gérant."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Gérant")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(1280, 768)
        self._init_catalog()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre d'administration."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        self._build_menu_bar()
        main_layout.addWidget(self.menubar)
        main_layout.addWidget(separator(QFrame.Shape.HLine))  # Ligne sous la barre de menu

        # Partie centrale
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)
        center_layout.addWidget(self._build_stocks_column(), stretch=0)
        center_layout.addWidget(separator(QFrame.Shape.VLine))
        center_layout.addWidget(self._build_plan_column(), stretch=2)
        center_layout.addWidget(separator(QFrame.Shape.VLine))
        center_layout.addWidget(self._build_tools_column(), stretch=0)
        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

    def _build_menu_bar(self):
        """Crée la barre de menu et le bouton de déconnexion."""
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

        self.btn_deconnexion = logout_button()
        self.menubar.setCornerWidget(self.btn_deconnexion, Qt.Corner.TopRightCorner)

    def _build_stocks_column(self):
        """Colonne gauche : gestion des stocks, filtre et recherche."""
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        gestion_frame = QFrame()
        gestion_layout = QVBoxLayout(gestion_frame)
        gestion_layout.setContentsMargins(8, 8, 8, 8)
        gestion_layout.setSpacing(6)
        gestion_layout.addWidget(bold_label("Gestion des stocks", 12))

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
        left_col.addWidget(bold_label("Filtre", 10))
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem(ALL_CATEGORIES)
        left_col.addWidget(self.filtre_combo)

        # Rechercher un article
        left_col.addWidget(bold_label("Rechercher", 10))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        left_col.addWidget(self.search_input)

        # Stocks
        left_col.addWidget(bold_label("Vos stocks", 11))
        self.stocks_list = DraggableListWidget()
        self.stocks_list.setDragEnabled(True)
        left_col.addWidget(self.stocks_list, stretch=1)

        left_col.addStretch()
        return wrap_in_side_frame(left_col)

    def _build_plan_column(self):
        """Colonne centrale : plan du magasin."""
        plan_col = QVBoxLayout()
        plan_col.addWidget(bold_label("Plan du magasin", 12))
        self.grid_overlay = GridOverlay()
        plan_col.addWidget(self.grid_overlay, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        return plan_widget

    def _build_tools_column(self):
        """Colonne droite : commandes, outils de dessin, zoom et taille de grille."""
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        comm_box = QGroupBox("Commandes")
        comm_box.setMinimumWidth(220)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_ouvrir_image = command_button("Ouvrir un plan", comm_layout)
        self.btn_reinitialiser = command_button("Réinitialiser", comm_layout)
        self.btn_exporter = command_button("Exporter en JSON", comm_layout)
        self.btn_importer = command_button("Importer en JSON", comm_layout)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        outils_box = QGroupBox("Outils")
        outils_box.setMinimumWidth(220)
        outils_layout = QVBoxLayout()
        outils_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_deplacer = command_button("Se déplacer", outils_layout)
        self.btn_rayon = command_button("Rayon", outils_layout)
        self.btn_stock = command_button("Stock", outils_layout)
        self.btn_caisse = command_button("Caisse", outils_layout)
        self.btn_entree = command_button("Entrée", outils_layout)
        self.btn_supprimer = command_button("Effacer", outils_layout)
        outils_box.setLayout(outils_layout)
        right_col.addWidget(outils_box)

        # Zoom et grille
        zoom_box, self.slider_grid, self.slider_zoom = zoom_group_box(self.grid_overlay, with_grid_size=True)
        right_col.addWidget(zoom_box)

        right_col.addStretch()
        return wrap_in_side_frame(right_col)

    def afficher_stocks_depuis_json(self, articles_json_content):
        """Affiche les stocks à partir d'un contenu JSON."""
        self._load_catalog(
            articles_json_content,
            status_ok="{count} produits chargés depuis la base de données.",
            empty_message="Aucun stock trouvé.",
            status_error="Erreur lors du chargement des articles.",
        )
