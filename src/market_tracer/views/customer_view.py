# ==============================================================
# Vue pour la fenêtre client & employé
# Développé par N. COLIN, D. MELOCCO
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMenuBar,
    QPushButton, QVBoxLayout, QWidget
)

from market_tracer.constants import ALL_CATEGORIES
from market_tracer.ui_helpers import (
    app_icon, bold_label, command_button, logout_button, separator,
    wrap_in_side_frame, zoom_group_box
)
from market_tracer.views.catalog_mixin import ProductCatalogMixin
from market_tracer.widgets.draggable_list import DraggableListWidget
from market_tracer.widgets.grid_overlay import GridOverlay


class CustomerView(ProductCatalogMixin, QWidget):
    """Vue pour la fenêtre client"""
    def __init__(self):
        """Initialise la vue client."""
        super().__init__()
        self.setWindowTitle("Market Tracer - Client & Employé")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(1280, 768)
        self._init_catalog()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre client."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        self._build_menu_bar()
        main_layout.addWidget(self.menubar)
        main_layout.addWidget(separator(QFrame.Shape.HLine))  # Ligne sous la barre de menu

        # Partie centrale
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)
        center_layout.addWidget(self._build_list_column(), stretch=0)
        center_layout.addWidget(separator(QFrame.Shape.VLine))
        center_layout.addWidget(self._build_plan_column(), stretch=2)
        center_layout.addWidget(separator(QFrame.Shape.VLine))
        center_layout.addWidget(self._build_route_column(), stretch=0)
        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

    def _build_menu_bar(self):
        """Crée la barre de menu et le bouton de déconnexion."""
        self.menubar = QMenuBar()
        self.fichier_menu = self.menubar.addMenu("Fichier")
        self.action_exporter = self.fichier_menu.addAction("Exporter ma liste")
        self.action_importer = self.fichier_menu.addAction("Importer une liste")

        self.aide_menu = self.menubar.addMenu("Aide")
        self.action_about = self.aide_menu.addAction("À propos")
        self.action_doc = self.aide_menu.addAction("Notice d'utilisation")
        self.action_licence = self.aide_menu.addAction("Licence")

        self.btn_deconnexion = logout_button()
        self.menubar.setCornerWidget(self.btn_deconnexion, Qt.Corner.TopRightCorner)

    def _build_list_column(self):
        """Colonne gauche : gestion de la liste de courses."""
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        liste_frame = QFrame()
        liste_layout = QVBoxLayout(liste_frame)
        liste_layout.setContentsMargins(8, 8, 8, 8)
        liste_layout.setSpacing(6)
        liste_layout.addWidget(bold_label("Liste de courses", 12))

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
        liste_layout.addWidget(bold_label("Filtre", 10))
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem(ALL_CATEGORIES)
        liste_layout.addWidget(self.filtre_combo)

        # Recherche d'article
        liste_layout.addWidget(bold_label("Rechercher", 10))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        liste_layout.addWidget(self.search_input)

        # Liste des produits disponibles
        liste_layout.addWidget(bold_label("Articles disponibles", 10))
        self.stocks_list = DraggableListWidget()
        self.stocks_list.setDragEnabled(False)
        liste_layout.addWidget(self.stocks_list, stretch=1)

        # Liste de courses du client
        liste_layout.addWidget(bold_label("Votre liste de courses", 11))
        self.courses_list = DraggableListWidget()
        self.courses_list.setDragEnabled(True)
        liste_layout.addWidget(self.courses_list, stretch=1)

        left_col.addWidget(liste_frame)
        left_col.addStretch()
        return wrap_in_side_frame(left_col)

    def _build_plan_column(self):
        """Colonne centrale : plan du magasin."""
        plan_col = QVBoxLayout()
        plan_col.addWidget(bold_label("Plan du magasin", 12))
        self.grid_overlay = GridOverlay()
        self.grid_overlay.set_pan_mode(True)
        self.grid_overlay.setInteractive(False)
        plan_col.addWidget(self.grid_overlay, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        return plan_widget

    def _build_route_column(self):
        """Colonne droite : commandes, parcours et zoom."""
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        comm_box = QGroupBox("Commandes")
        comm_box.setMinimumWidth(220)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_vider_liste = command_button("Vider ma liste", comm_layout)
        self.btn_exporter = command_button("Exporter ma liste", comm_layout)
        self.btn_importer = command_button("Importer une liste", comm_layout)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        parcours_box = QGroupBox("Parcours")
        parcours_box.setMinimumWidth(220)
        parcours_layout = QVBoxLayout()
        parcours_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_generer = command_button("Générer le parcours", parcours_layout)
        parcours_box.setLayout(parcours_layout)
        right_col.addWidget(parcours_box)

        # Zoom
        zoom_box, _, self.slider_zoom = zoom_group_box(self.grid_overlay, with_grid_size=False)
        right_col.addWidget(zoom_box)

        right_col.addStretch()
        return wrap_in_side_frame(right_col)

    def afficher_produits_depuis_json(self, produits_json_content):
        """Affiche les produits à partir d'un contenu JSON."""
        self._load_catalog(
            produits_json_content,
            status_ok="{count} produits chargés.",
            empty_message="Aucun produit trouvé.",
            status_error="Erreur lors du chargement des produits.",
        )
