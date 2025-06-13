# ==============================================================

# Market Tracer - Page gérant
# Développé par Lysandre Pace--Boulnois
# Dernière modification : 12/06/2025

# ==============================================================

# Importations
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QListWidget,
    QLineEdit, QGroupBox, QMenuBar, QComboBox, QMessageBox, QFileDialog, QSlider
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
import json
import sqlite3
import platform
from addArticleDialog import AddArticleDialog
from shopManagerDialog import ShopManagerDialog
from employeeManagerDialog import EmployeeManagerDialog
from quadrillage import GridOverlay, DraggableListWidget

# ==============================================================
# Fenêtre principale du gérant
# ==============================================================

class AdminWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Market Tracer - Admin")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)
        self.categories = set()
        self.produit_categorie_map = {}
        self.setup_ui()

    # Initialise l'interface principale
    def setup_ui(self):
        print("[AdminWindow] Construction de l'UI")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Menu déroulant
        menubar = QMenuBar()
        fichier_menu = menubar.addMenu("Fichier")
        fichier_menu.addAction("Ouvrir")
        action_charger = fichier_menu.addAction("Charger")
        action_charger.triggered.connect(self.ouvrir_gestion_magasins)
        fichier_menu.addAction("Fermer")
        fichier_menu.addAction("Exporter")

        gestion_menu = menubar.addMenu("Gestion")
        action_modifier_magasin = gestion_menu.addAction("Modifier mon magasin")
        action_modifier_magasin.triggered.connect(self.ouvrir_modifier_magasin)
        action_gestion_employes = gestion_menu.addAction("Gérer les employés")
        action_gestion_employes.triggered.connect(self.ouvrir_gestion_employes)

        plan_menu = menubar.addMenu("Plan")
        plan_menu.addAction("Ouvrir")
        plan_menu.addAction("Afficher")
        plan_menu.addAction("Paramétrer")

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
        btn_retirer.clicked.connect(self.retirer_article_selectionne)
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
        self.stocks_list.itemClicked.connect(self.afficher_details_produit)

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

        # Colonne centrale (Plan)
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

        # Colonne droite (Commandes, Outils, Zoom, Détail)
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        comm_box = QGroupBox("Commandes")
        comm_box.setMinimumWidth(220)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(10, 10, 10, 10)
        btn_ouvrir_image = QPushButton("Ouvrir une image")
        btn_ouvrir_image.setMinimumHeight(25)
        btn_ouvrir_image.clicked.connect(self.ouvrir_image_plan)
        comm_layout.addWidget(btn_ouvrir_image)
        btn_reinitialiser = QPushButton("Réinitialiser")
        btn_reinitialiser.setMinimumHeight(25)
        btn_reinitialiser.clicked.connect(self.grid_overlay.reset_colored_cells)
        comm_layout.addWidget(btn_reinitialiser)
        btn_exporter = QPushButton("Exporter en JSON")
        btn_exporter.setMinimumHeight(25)
        btn_exporter.clicked.connect(self.exporter_quadrillage_json)
        comm_layout.addWidget(btn_exporter)
        btn_importer = QPushButton("Importer en JSON")
        btn_importer.setMinimumHeight(25)
        btn_importer.clicked.connect(self.importer_quadrillage_json)
        comm_layout.addWidget(btn_importer)
        btn_charger = QPushButton("Charger JSON Objets")
        btn_charger.setMinimumHeight(25)
        btn_charger.clicked.connect(self.charger_objets_json)
        comm_layout.addWidget(btn_charger)
        comm_box.setLayout(comm_layout)
        right_col.addWidget(comm_box)

        outils_box = QGroupBox("Outils")
        outils_box.setMinimumWidth(220)
        outils_layout = QVBoxLayout()
        outils_layout.setContentsMargins(10, 10, 10, 10)
        btn_rayon = QPushButton("Rayon (bleu)")
        btn_rayon.setMinimumHeight(25)
        btn_rayon.clicked.connect(lambda: self.grid_overlay.set_current_color('Rayon'))
        outils_layout.addWidget(btn_rayon)
        btn_caisse = QPushButton("Caisse (jaune)")
        btn_caisse.setMinimumHeight(25)
        btn_caisse.clicked.connect(lambda: self.grid_overlay.set_current_color('Caisse'))
        outils_layout.addWidget(btn_caisse)
        btn_entree = QPushButton("Entrée (Rouge)")
        btn_entree.setMinimumHeight(25)
        btn_entree.clicked.connect(lambda: self.grid_overlay.set_current_color('Entrée'))
        outils_layout.addWidget(btn_entree)
        btn_mur = QPushButton("Mur (Gris)")
        btn_mur.setMinimumHeight(25)
        btn_mur.clicked.connect(lambda: self.grid_overlay.set_current_color('Mur'))
        outils_layout.addWidget(btn_mur)
        btn_gomme = QPushButton("Gomme")
        btn_gomme.setMinimumHeight(25)
        btn_gomme.clicked.connect(lambda: self.grid_overlay.set_current_color('Gomme'))
        outils_layout.addWidget(btn_gomme)
        btn_deplacer = QPushButton("Se déplacer")
        btn_deplacer.setMinimumHeight(25)
        btn_deplacer.clicked.connect(lambda: self.grid_overlay.set_pan_mode(True))
        outils_layout.addWidget(btn_deplacer)
        # Désactive le mode déplacement pour les autres boutons
        for b in [btn_rayon, btn_caisse, btn_entree, btn_mur, btn_gomme]:
            b.clicked.connect(lambda: self.grid_overlay.set_pan_mode(False))
        outils_box.setLayout(outils_layout)
        right_col.addWidget(outils_box)

        zoom_box = QGroupBox("Zoom")
        zoom_box.setMinimumWidth(220)
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(10, 10, 10, 10)
        label_zoom_grid = QLabel("Zoom grille :\nAjuste la taille des cases de la grille")
        label_zoom_grid.setWordWrap(True)
        zoom_layout.addWidget(label_zoom_grid)
        self.slider_grid = QSlider(Qt.Orientation.Horizontal)
        self.slider_grid.setMinimum(25)
        self.slider_grid.setMaximum(100)
        self.slider_grid.setValue(self.grid_overlay.grid_size)
        self.slider_grid.valueChanged.connect(lambda v: self.grid_overlay.set_grid_size(v))
        zoom_layout.addWidget(self.slider_grid)
        label_zoom_global = QLabel("Zoom global :\nAgrandit ou réduit tout le plan")
        label_zoom_global.setWordWrap(True)
        zoom_layout.addWidget(label_zoom_global)
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(10)
        self.slider_zoom.setMaximum(300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(lambda v: self.grid_overlay.set_zoom(v / 100.0))
        zoom_layout.addWidget(self.slider_zoom)
        zoom_box.setLayout(zoom_layout)
        right_col.addWidget(zoom_box)

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
                self.afficher_stocks_depuis_json(articles_json)
            else:
                self.status_bar.setText("Aucun article associé à ce magasin.")
            if plan_image_path:
                self.grid_overlay.load_image(plan_image_path)
            if plan_json:
                self.grid_overlay.import_cells_from_json_content(plan_json)
        else:
            self.status_bar.setText("Aucun magasin associé à ce compte.")

    def ouvrir_fichier_json(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Fichiers JSON (*.json)")
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                with open(filenames[0], "r", encoding="utf-8") as f:
                    content = f.read()
                self.afficher_stocks_depuis_json(content)
                self.status_bar.setText(f"Fichier chargé : {filenames[0]}")

    def afficher_stocks_depuis_json(self, articles_json_content):
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            if isinstance(articles_json_content, str) and articles_json_content.endswith(".json"):
                with open(articles_json_content, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(articles_json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    text = f"{produit}"
                    self.stocks_list.addItem(text)
                    self.produit_categorie_map[text] = categorie
            self.filtre_combo.blockSignals(True)
            self.filtre_combo.clear()
            self.filtre_combo.addItem("Toutes les catégories")
            for cat in sorted(self.categories):
                self.filtre_combo.addItem(cat)
            self.filtre_combo.blockSignals(False)
            self.status_bar.setText(f"{self.stocks_list.count()} produits chargés depuis la base de données.")
        except Exception as e:
            self.stocks_list.addItem("Erreur de lecture du JSON")
            self.status_bar.setText("Erreur lors du chargement des articles.")

    # Affiche les détails du produit sélectionné
    def afficher_details_produit(self, item):
        produit = item.text()
        categorie = self.produit_categorie_map.get(produit, "Inconnu")
        self.produit_label.setText(f"Produit : {produit}")
        self.categorie_label.setText(f"Catégorie : {categorie}")

    # Filtre la liste des articles selon la catégorie
    def filtrer_stocks(self, categorie):
        self.stocks_list.clear()
        texte = self.search_input.text().lower() if hasattr(self, "search_input") else ""
        for produit, cat in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in produit.lower():
                self.stocks_list.addItem(produit)

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
                text = f"{categorie}::{nom}"
                self.stocks_list.addItem(text)
                self.produit_categorie_map[text] = categorie
                self.categories.add(categorie)
                self.status_bar.setText(f"Article '{nom}' ajouté à la catégorie '{categorie}'.")
                self.filtre_combo.blockSignals(True)
                self.filtre_combo.clear()
                self.filtre_combo.addItem("Toutes les catégories")
                for cat in sorted(self.categories):
                    self.filtre_combo.addItem(cat)
                self.filtre_combo.blockSignals(False)
                # Mise à jour du JSON en BDD
                self.sauvegarder_articles_json()
            else:
                QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

    def retirer_article_selectionne(self):
        item = self.stocks_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return
        nom = item.text()
        categorie = self.produit_categorie_map.get(nom)
        if categorie and nom in self.produit_categorie_map:
            del self.produit_categorie_map[nom]
        self.stocks_list.takeItem(self.stocks_list.row(item))
        # Mise à jour du JSON en BDD
        self.sauvegarder_articles_json()
        self.status_bar.setText(f"Article '{nom}' retiré du stock.")

    def sauvegarder_articles_json(self):
        # Reconstruit le JSON à partir de la map
        data = {}
        for produit, categorie in self.produit_categorie_map.items():
            cat, prod = produit.split("::", 1)
            data.setdefault(cat, []).append(prod)
        articles_json_content = json.dumps(data, ensure_ascii=False, indent=2)
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("UPDATE shops SET articles_json=? WHERE user_id=?", (articles_json_content, self.user_id))
        conn.commit()
        conn.close()

    def ouvrir_modifier_magasin(self):
        from createShopWindow import CreateShopWindow
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
            self.status_bar.setText("Magasin modifié avec succès.")
            self.afficher_stocks_depuis_json(dialog.json_input.text())

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_overlay.load_image(file_name)
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("UPDATE shops SET chemin=? WHERE user_id=?", (file_name, self.user_id))
            conn.commit()
            conn.close()
            self.sauvegarder_plan_et_quadrillage()

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

# Lancement de l'application

# ==============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if is_dark_theme():
        app.setStyle("Fusion")
        dark_palette = app.palette()
        dark_palette.setColor(dark_palette.Window, Qt.GlobalColor.black)
        dark_palette.setColor(dark_palette.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.Base, Qt.GlobalColor.black)
        dark_palette.setColor(dark_palette.AlternateBase, Qt.GlobalColor.black)
        dark_palette.setColor(dark_palette.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.Text, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.Button, Qt.GlobalColor.black)
        dark_palette.setColor(dark_palette.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(dark_palette.Highlight, Qt.GlobalColor.darkGray)
        dark_palette.setColor(dark_palette.HighlightedText, Qt.GlobalColor.black)
        app.setPalette(dark_palette)
    else:
        app.setStyle("Fusion")
    sys.exit(app.exec())