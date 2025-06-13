# ==============================================================

# Market Tracer - Page Gérant
# Développé par Lysandre Pace--Boulnois
# Dernière modification : 12/06/2025

# ==============================================================

# Importations
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLineEdit, QGroupBox, QMenuBar, QComboBox, QMessageBox, QFileDialog, QSlider
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import sys, json, sqlite3, platform, os
from addArticleDialog import AddArticleDialog
from shopManagerDialog import ShopManagerDialog
from employeeManagerDialog import EmployeeManagerDialog
from quadrillage import GridOverlay, DraggableListWidget
from createShopWindow import CreateShopWindow

# ==============================================================
# Fenêtre principale du gérant
# ==============================================================
class AdminWindow(QWidget):
    """Fenêtre principale pour le gérant du magasin."""
    def __init__(self, user_id):
        """Initialise la fenêtre principale du gérant.

        Args:
            user_id (int): ID de l'utilisateur connecté.
        """
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Market Tracer - Gérant")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setMinimumSize(1280, 768)
        self.categories = set()
        self.produit_categorie_map = {}
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre principale."""
        print("[AdminWindow] Construction de l'UI")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Menu déroulant
        menubar = QMenuBar()
        fichier_menu = menubar.addMenu("Fichier")
        action_charger = fichier_menu.addAction("Charger")
        action_charger.triggered.connect(self.ouvrir_gestion_magasins)
        fichier_menu.addAction("Sauvegarder")

        gestion_menu = menubar.addMenu("Gestion")
        action_configurer = gestion_menu.addAction("Configurer mon magasin")
        action_configurer.triggered.connect(self.ouvrir_configurer_magasin)
        action_gestion_employes = gestion_menu.addAction("Gérer les employés")
        action_gestion_employes.triggered.connect(self.ouvrir_gestion_employes)

        plan_menu = menubar.addMenu("Plan")
        plan_menu.addAction("Ouvrir")
        plan_menu.addAction("Afficher")

        aide_menu = menubar.addMenu("Aide")
        action_about = aide_menu.addAction("À propos")
        action_doc = aide_menu.addAction("Documentation")
        action_licence = aide_menu.addAction("Licence")
        action_about.triggered.connect(self.open_about)
        action_doc.triggered.connect(self.open_doc)
        action_licence.triggered.connect(self.open_licence)

        btn_deconnexion = QPushButton("Déconnexion")
        btn_deconnexion.setStyleSheet("background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;")
        btn_deconnexion.clicked.connect(self.deconnexion)
        menubar.setCornerWidget(btn_deconnexion, Qt.Corner.TopRightCorner)
        main_layout.addWidget(menubar)

        # Barre horizontale sous la barre de menus
        hline_menu = QFrame()
        hline_menu.setFrameShape(QFrame.Shape.HLine)
        hline_menu.setFrameShadow(QFrame.Shadow.Sunken)
        hline_menu.setLineWidth(1)
        hline_menu.setMidLineWidth(0)
        main_layout.addWidget(hline_menu)

        # Partie centrale
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)

        # Colonne gauche (Stocks)
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        gestion_frame = QFrame()
        gestion_layout = QVBoxLayout(gestion_frame)
        gestion_layout.setContentsMargins(8, 8, 8, 8)
        gestion_layout.setSpacing(6)
        gestion_label = QLabel("Gestion des stocks")
        gestion_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        gestion_layout.addWidget(gestion_label)

        btn_ajouter = QPushButton("Ajouter à mon stock")
        btn_ajouter.setFixedHeight(28)
        btn_ajouter.setStyleSheet("background: #56E39F; ")
        btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout_article)
        gestion_layout.addWidget(btn_ajouter)

        btn_retirer = QPushButton("Retirer de mon stock")
        btn_retirer.setFixedHeight(28)
        btn_retirer.setStyleSheet("background: #FF6B3D; ")
        btn_retirer.clicked.connect(self.confirm_remove)
        gestion_layout.addWidget(btn_retirer)
        left_col.addWidget(gestion_frame)

        filtre_label = QLabel("Filtre")
        filtre_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(filtre_label)
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem("Toutes les catégories")
        self.filtre_combo.currentTextChanged.connect(self.filtrer_stocks)
        left_col.addWidget(self.filtre_combo)

        search_label = QLabel("Rechercher")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        self.search_input.textChanged.connect(self.rechercher_stocks)
        left_col.addWidget(self.search_input)

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
        btn_ouvrir_image = QPushButton("Ouvrir un plan")
        btn_ouvrir_image.setMinimumHeight(25)
        btn_ouvrir_image.clicked.connect(self.ouvrir_image_plan)
        comm_layout.addWidget(btn_ouvrir_image)
        btn_reinitialiser = QPushButton("Réinitialiser")
        btn_reinitialiser.setMinimumHeight(25)
        btn_reinitialiser.clicked.connect(self.confirm_reset)
        comm_layout.addWidget(btn_reinitialiser)
        btn_exporter = QPushButton("Exporter en JSON")
        btn_exporter.setMinimumHeight(25)
        btn_exporter.clicked.connect(self.exporter_quadrillage_json)
        comm_layout.addWidget(btn_exporter)
        btn_importer = QPushButton("Importer en JSON")
        btn_importer.setMinimumHeight(25)
        btn_importer.clicked.connect(self.importer_quadrillage_json)
        comm_layout.addWidget(btn_importer)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        outils_box = QGroupBox("Outils")
        outils_box.setMinimumWidth(220)
        outils_layout = QVBoxLayout()
        outils_layout.setContentsMargins(10, 10, 10, 10)
        btn_deplacer = QPushButton("Se déplacer")
        btn_deplacer.setMinimumHeight(25)
        btn_deplacer.clicked.connect(lambda: self.grid_overlay.set_pan_mode(True))
        outils_layout.addWidget(btn_deplacer)
        btn_rayon = QPushButton("Rayon")
        btn_rayon.setMinimumHeight(25)
        btn_rayon.clicked.connect(lambda: self.grid_overlay.set_current_color('Rayon'))
        outils_layout.addWidget(btn_rayon)
        btn_caisse = QPushButton("Caisse")
        btn_caisse.setMinimumHeight(25)
        btn_caisse.clicked.connect(lambda: self.grid_overlay.set_current_color('Caisse'))
        outils_layout.addWidget(btn_caisse)
        btn_entree = QPushButton("Entrée")
        btn_entree.setMinimumHeight(25)
        btn_entree.clicked.connect(lambda: self.grid_overlay.set_current_color('Entrée'))
        outils_layout.addWidget(btn_entree)
        btn_mur = QPushButton("Mur")
        btn_mur.setMinimumHeight(25)
        btn_mur.clicked.connect(lambda: self.grid_overlay.set_current_color('Mur'))
        outils_layout.addWidget(btn_mur)
        btn_gomme = QPushButton("Gomme")
        btn_gomme.setMinimumHeight(25)
        btn_gomme.clicked.connect(lambda: self.grid_overlay.set_current_color('Gomme'))
        outils_layout.addWidget(btn_gomme)

        # Désactive le mode déplacement pour les autres boutons
        for b in [btn_rayon, btn_caisse, btn_entree, btn_mur, btn_gomme]:
            b.clicked.connect(lambda: self.grid_overlay.set_pan_mode(False))
        outils_box.setLayout(outils_layout)
        right_col.addWidget(outils_box)

        zoom_box = QGroupBox("Zoom")
        zoom_box.setMinimumWidth(220)
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(10, 10, 10, 10)
        label_grid_size = QLabel("Grille :\nAjuste la taille des cases de la grille")
        label_grid_size.setWordWrap(True)
        zoom_layout.addWidget(label_grid_size)
        self.slider_grid = QSlider(Qt.Orientation.Horizontal)
        self.slider_grid.setMinimum(25)
        self.slider_grid.setMaximum(100)
        self.slider_grid.setValue(self.grid_overlay.grid_size)
        self.slider_grid.valueChanged.connect(lambda v: self.grid_overlay.set_grid_size(v))
        zoom_layout.addWidget(self.slider_grid)
        label_zoom = QLabel("Zoom :\nAgrandit ou réduit le plan")
        label_zoom.setWordWrap(True)
        zoom_layout.addWidget(label_zoom)
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(10)
        self.slider_zoom.setMaximum(300)
        self.slider_zoom.setValue(50)
        self.slider_zoom.valueChanged.connect(lambda v: self.grid_overlay.set_zoom(v / 100.0))
        self.grid_overlay.set_zoom(0.5)
        zoom_layout.addWidget(self.slider_zoom)
        zoom_box.setLayout(zoom_layout)
        right_col.addWidget(zoom_box)

        right_col.addStretch()
        right_frame = QFrame()
        right_frame.setLayout(right_col)
        right_frame.setMinimumWidth(260)
        right_frame.setMaximumWidth(340)
        center_layout.addWidget(right_frame, stretch=0)

        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

        # Connexion du signal de sauvegarde automatique du quadrillage
        self.grid_overlay.grid_modified.connect(self.sauvegarder_plan_et_quadrillage)

        # Chargement des données du magasin
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT articles_json, plan_json, chemin FROM shops WHERE user_id=?", (self.user_id,))
        result = c.fetchone()
        conn.close()
        if result:
            articles_json, plan_json, plan_image_path = result
            if articles_json:
                # Si c'est un chemin de fichier JSON, on lit le contenu
                if isinstance(articles_json, str) and articles_json.endswith('.json') and os.path.isfile(articles_json):
                    with open(articles_json, "r", encoding="utf-8") as f:
                        articles_json_content = f.read()
                else:
                    articles_json_content = articles_json
                self.afficher_stocks_depuis_json(articles_json_content)
            else:
                self.status_bar.setText("Aucun article associé à ce magasin.")
            if plan_image_path:
                self.grid_overlay.load_image(plan_image_path)
            else:
                self.status_bar.setText("Aucun plan associé à ce magasin.")
            if plan_json:
                self.grid_overlay.import_cells_from_json_content(plan_json)
                self.slider_grid.setValue(self.grid_overlay.grid_size)
            else:
                self.status_bar.setText("Aucun quadrillage associé à ce magasin.")
        else:
            self.status_bar.setText("Aucun magasin associé à ce compte.")

    def ouvrir_gestion_magasins(self):
        dlg = ShopManagerDialog(self.user_id, self)
        if dlg.exec():
            if hasattr(dlg, "creation_demande") and dlg.creation_demande:
                self.creer_nouveau_magasin()
            elif hasattr(dlg, "selected_shop_id"):
                self.charger_magasin_existant(dlg.selected_shop_id)
                
    def creer_nouveau_magasin(self):
        dialog = CreateShopWindow(self.user_id, self, None)
        if dialog.exec():
            # Après la création, récupérons l'ID du nouveau shop
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("SELECT id, articles_json, plan_json, chemin FROM shops WHERE user_id=? ORDER BY id DESC LIMIT 1", (self.user_id,))
            result = c.fetchone()
            conn.close()
            if result:
                shop_id, articles_json, plan_json, plan_image_path = result
                self.charger_magasin_existant(shop_id)
                
    def charger_magasin_existant(self, shop_id):
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT articles_json, plan_json, chemin FROM shops WHERE id=?", (shop_id,))
        result = c.fetchone()
        conn.close()
        if result:
            articles_json, plan_json, plan_image_path = result
            if articles_json:
                if isinstance(articles_json, str) and articles_json.endswith('.json') and os.path.isfile(articles_json):
                    with open(articles_json, "r", encoding="utf-8") as f:
                        articles_json_content = f.read()
                else:
                    articles_json_content = articles_json
                self.afficher_stocks_depuis_json(articles_json_content)
            else:
                self.status_bar.setText("Aucun article associé à ce magasin.")
            if plan_image_path:
                self.grid_overlay.load_image(plan_image_path)
            else:
                self.status_bar.setText("Aucun plan associé à ce magasin.")
            if plan_json:
                self.grid_overlay.import_cells_from_json_content(plan_json)
                self.slider_grid.setValue(self.grid_overlay.grid_size)
            else:
                self.status_bar.setText("Aucun quadrillage associé à ce magasin.")
        else:
            QMessageBox.warning(self, "Erreur", "Magasin introuvable.")




    def afficher_stocks_depuis_json(self, articles_json_content):
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            data = json.loads(articles_json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    key = f"{categorie.lower()}::{produit.lower()}"
                    self.stocks_list.addItem(f"{produit}")
                    self.produit_categorie_map[key] = (categorie, produit)
            self._maj_filtre_categories()
            self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis la base de données.")
        except Exception as e:
            self.stocks_list.addItem("Erreur de lecture du JSON")
            self.status_bar.setText("Erreur lors du chargement des articles.")

    # Filtre la liste des articles selon la catégorie
    def filtrer_stocks(self, categorie):
        self.stocks_list.clear()
        texte = self.search_input.text().lower() if hasattr(self, "search_input") else ""
        for key, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat.lower() == categorie.lower()) and texte in nom.lower():
                self.stocks_list.addItem(f"{cat}::{nom}")

    # Déconnecte l'utilisateur
    def deconnexion(self):
        from main import LoginWindow
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def ouvrir_dialog_ajout_article(self):
        dialog = AddArticleDialog(self.categories, self)
        if dialog.exec():
            nom, categorie = dialog.get_data()
            if nom and categorie:
                key = f"{categorie.lower()}::{nom.lower()}"  # clé insensible à la casse
                text = f"{categorie}::{nom}"  # affichage d'origine
                self.stocks_list.addItem(text)
                self.produit_categorie_map[key] = (categorie, nom)  # stocke l'affichage d'origine
                self.categories.add(categorie)
                self.status_bar.setText(f"Article '{nom}' ajouté à la catégorie '{categorie}'.")
                self._maj_filtre_categories()
                self.sauvegarder_articles_json()
            else:
                QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

    def retirer_article_selectionne(self):
        item = self.stocks_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return
        text = item.text()
        cat, nom = text.split("::", 1)
        key = f"{cat.lower()}::{nom.lower()}"
        if key in self.produit_categorie_map:
            
            del self.produit_categorie_map[key]
        self.stocks_list.takeItem(self.stocks_list.row(item))
        self.sauvegarder_articles_json()
        self.status_bar.setText(f"Article '{nom}' retiré du stock.")

    def sauvegarder_articles_json(self):
        data = {}
        for key, (cat, nom) in self.produit_categorie_map.items():
            data.setdefault(cat, []).append(nom)
        articles_json_content = json.dumps(data, ensure_ascii=False, indent=2)
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("UPDATE shops SET articles_json=? WHERE user_id=?", (articles_json_content, self.user_id))
        conn.commit()
        conn.close()

    def ouvrir_configurer_magasin(self):
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT nom, auteur, date_creation, apropos, chemin, articles_json FROM shops WHERE user_id=?", (self.user_id,))
        row = c.fetchone()
        conn.close()
        shop_data = None
        if row:
            shop_data = {
                "nom": row[0],
                "auteur": row[1],
                "date_creation": row[2],
                "apropos": row[3],
                "chemin": row[4],
                "articles_json": row[5]
            }
        dialog = CreateShopWindow(self.user_id, self, shop_data)
        if dialog.exec():
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("SELECT chemin FROM shops WHERE user_id=?", (self.user_id,))
            row = c.fetchone()
            path = row[0] if row else None

            self.grid_overlay.load_image(path)
            json_path = dialog.json_input.text()
            if json_path and json_path.endswith('.json') and os.path.isfile(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    articles_json_content = f.read()
            else:
                articles_json_content = json_path
            self.afficher_stocks_depuis_json(articles_json_content)
            self.status_bar.setText("Magasin modifié avec succès.")

    def rechercher_stocks(self, texte):
        texte = texte.lower()
        categorie = self.filtre_combo.currentText()
        self.stocks_list.clear()
        for produit, cat in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in produit.lower():
                self.stocks_list.addItem(produit)

    def ouvrir_gestion_employes(self):
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id FROM shops WHERE user_id=?", (self.user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            shop_id = row[0]
            dlg = EmployeeManagerDialog(shop_id, self)
            dlg.exec()
        else:
            QMessageBox.warning(self, "Erreur", "Aucun magasin associé à ce compte.")

    def ouvrir_gestion_magasins(self):
        dlg = ShopManagerDialog(self.user_id, self)
        if dlg.exec() and hasattr(dlg, "selected_shop_id"):
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("SELECT articles_json FROM shops WHERE id=?", (dlg.selected_shop_id,))
            result = c.fetchone()
            conn.close()
            if result and result[0]:
                self.afficher_stocks_depuis_json(result[0])
                self.status_bar.setText("Magasin chargé.")
            else:
                self.status_bar.setText("Aucun article associé à ce magasin.")

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

    def ouvrir_image_plan(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir un plan", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_overlay.load_image(file_name)
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("UPDATE shops SET chemin=? WHERE user_id=?", (file_name, self.user_id))
            conn.commit()
            conn.close()
            self.sauvegarder_plan_et_quadrillage()

    def confirm_reset(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Êtes-vous sûr de vouloir tout réinitialiser ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.grid_overlay.reset_colored_cells()

    def confirm_remove(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Êtes-vous sûr de vouloir retirer ce produit ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.retirer_article_selectionne()

    def exporter_quadrillage_json(self):
        if self.grid_overlay.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'exporter un JSON.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Exporter en JSON", "", "JSON (*.json)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                import io
                buffer = io.StringIO()
                self.grid_overlay.export_cells_to_json(buffer)
                f.write(buffer.getvalue())
                buffer.close()
            QMessageBox.information(self, "Export", "Exportation réussie !")

    def importer_quadrillage_json(self):
        if self.grid_overlay.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'importer un JSON.")
            return
        file_name, _ = QFileDialog.getOpenFileName(self, "Importer JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_overlay.import_cells_from_json(file_name)
            QMessageBox.information(self, "Import", "Importation réussie !")
            self.sauvegarder_plan_et_quadrillage()

    def charger_objets_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Charger un JSON d'objets", "", "JSON (*.json)")
        if not file_name:
            return
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            QMessageBox.information(self, "Objets chargés", f"{len(data) if isinstance(data, list) else 'Plusieurs'} objets chargés.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de chargement JSON : {e}")

    def sauvegarder_plan_et_quadrillage(self):
        plan_image_path = None
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT chemin FROM shops WHERE user_id=?", (self.user_id,))
        row = c.fetchone()
        if row:
            plan_image_path = row[0]
        import io
        buffer = io.StringIO()
        self.grid_overlay.export_cells_to_json(buffer)
        plan_json_content = buffer.getvalue()
        buffer.close()
        c.execute("UPDATE shops SET chemin=?, plan_json=? WHERE user_id=?", (plan_image_path, plan_json_content, self.user_id))
        conn.commit()
        conn.close()

    def _maj_filtre_categories(self):
        self.filtre_combo.blockSignals(True)
        self.filtre_combo.clear()
        self.filtre_combo.addItem("Toutes les catégories")
        for cat in sorted(self.categories, key=lambda x: x.lower()):
            self.filtre_combo.addItem(cat)
        self.filtre_combo.blockSignals(False)

# ==============================================================

# Fonction pour détecter le thème sombre du système

# ==============================================================

def is_dark_theme():
    import os
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False
    elif platform.system() == "Darwin":
        try:
            from subprocess import check_output
            result = check_output(
                ["defaults", "read", "-g", "AppleInterfaceStyle"], universal_newlines=True
            )
            return "Dark" in result
        except Exception:
            return False
    else:
        try:
            from subprocess import check_output
            theme = check_output(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"], universal_newlines=True
            )
            return "dark" in theme.lower()
        except Exception:
            return False

# ==============================================================

# Programme principal pour débogage

# ==============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AdminWindow(1)
    win.show()
    sys.exit(app.exec())