# ==============================================================
# Market Tracer - Page gérant
# ==============================================================
# Importations
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QListWidget,
    QLineEdit, QCheckBox, QSpinBox, QGroupBox, QMenuBar, QComboBox,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import sys
import json
import sqlite3
import platform
# ==============================================================
# Fenêtre d'ajout d'article

class AddArticleDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un article")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.setMinimumWidth(300)
        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        layout.addRow("Nom de l'article :", self.nom_input)

        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(sorted(categories) if categories else [])
        layout.addRow("Catégorie :", self.categorie_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.nom_input.text(), self.categorie_combo.currentText()

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
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # Menu déroulant
        menubar = QMenuBar()

        # Fichier
        fichier_menu = menubar.addMenu("Fichier")
        fichier_menu.addAction("Ouvrir")
        fichier_menu.addAction("Charger")
        fichier_menu.addAction("Fermer")
        fichier_menu.addAction("Exporter")

        # Gestion
        gestion_menu = menubar.addMenu("Gestion")
        action_modifier_magasin = gestion_menu.addAction("Modifier mon magasin")
        action_modifier_magasin.triggered.connect(self.ouvrir_modifier_magasin)
        action_gestion_employes = gestion_menu.addAction("Gérer les employés")
        action_gestion_employes.triggered.connect(self.ouvrir_gestion_employes)

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

        # Bouton déconnexion
        btn_deconnexion = QPushButton("Déconnexion")
        btn_deconnexion.setStyleSheet("background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;")
        btn_deconnexion.clicked.connect(self.deconnexion)
        menubar.setCornerWidget(btn_deconnexion, Qt.Corner.TopRightCorner)

        main_layout.addWidget(menubar)

        # === Barre horizontale sous la barre de menus ===
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

        # Zone gestion des stocks avec fond distinct
        gestion_frame = QFrame()
        gestion_layout = QVBoxLayout(gestion_frame)
        gestion_layout.setContentsMargins(8, 8, 8, 8)
        gestion_layout.setSpacing(6)

        gestion_label = QLabel("Gestion des stocks")
        gestion_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        gestion_layout.addWidget(gestion_label)

        # Boutons stock plus petits
        btn_ajouter = QPushButton("Ajouter à mon stock")
        btn_ajouter.setObjectName("btn_ajouter")
        btn_ajouter.setFixedHeight(28)
        btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout_article)
        gestion_layout.addWidget(btn_ajouter)

        btn_retirer = QPushButton("Retirer de mon stock")
        btn_retirer.setObjectName("btn_retirer")
        btn_retirer.setFixedHeight(28)
        btn_retirer.clicked.connect(self.retirer_article_selectionne)
        gestion_layout.addWidget(btn_retirer)

        left_col.addWidget(gestion_frame)

        # Filtre par catégorie
        filtre_label = QLabel("Filtre")
        filtre_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(filtre_label)

        self.filtre_combo = QComboBox()
        self.filtre_combo.addItem("Toutes les catégories")
        self.filtre_combo.currentTextChanged.connect(self.filtrer_stocks)
        left_col.addWidget(self.filtre_combo)

        # Label "Rechercher" 
        search_label = QLabel("Rechercher")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_col.addWidget(search_label)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article...")
        self.search_input.textChanged.connect(self.rechercher_stocks)
        left_col.addWidget(self.search_input)

        # Vos stocks
        stocks_label = QLabel("Vos stocks")
        stocks_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_col.addWidget(stocks_label)

        # Bouton pour choisir un fichier JSON
        btn_choisir_fichier = QPushButton("Choisir un fichier JSON")
        btn_choisir_fichier.clicked.connect(self.ouvrir_fichier_json)
        left_col.addWidget(btn_choisir_fichier)

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

        # === Barre verticale de séparation gauche-centre ===
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
        plan_frame = QFrame()
        plan_frame.setMinimumSize(600, 400)
        plan_col.addWidget(plan_frame, stretch=1)
        plan_col.addStretch()
        plan_widget = QWidget()
        plan_widget.setLayout(plan_col)
        center_layout.addWidget(plan_widget, stretch=2)

        # === Barre verticale de séparation centre-droite ===
        vline2 = QFrame()
        vline2.setFrameShape(QFrame.Shape.VLine)
        vline2.setFrameShadow(QFrame.Shadow.Sunken)
        vline2.setLineWidth(1)
        vline2.setMidLineWidth(0)
        center_layout.addWidget(vline2)

        # Colonne droite
        right_col = QVBoxLayout()
        right_col.setSpacing(18)  

        # Plan
        plan_box = QGroupBox("Plan")
        plan_box.setMinimumWidth(220)
        plan_box_layout = QVBoxLayout()
        plan_box_layout.setContentsMargins(10, 10, 10, 10)  
        plan_file_input = QLineEdit("Choisissez un fichier")
        plan_box_layout.addWidget(plan_file_input)
        plan_box.setLayout(plan_box_layout)
        right_col.addWidget(plan_box)

        # Espacement entre les blocs
        right_col.addSpacing(10)

        # Quadrillage
        grid_box = QGroupBox("Quadrillage")
        grid_box.setMinimumWidth(220)
        grid_layout = QVBoxLayout()
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_checkbox = QCheckBox("Afficher le quadrillage")
        grid_layout.addWidget(grid_checkbox)
        grid_pos_label = QLabel("Position du quadrillage")
        grid_layout.addWidget(grid_pos_label)
        pos_layout = QHBoxLayout()
        x_label = QLabel("x :")
        pos_layout.addWidget(x_label)
        x_spin = QSpinBox()
        pos_layout.addWidget(x_spin)
        y_label = QLabel("y :")
        pos_layout.addWidget(y_label)
        y_spin = QSpinBox()
        pos_layout.addWidget(y_spin)
        grid_layout.addLayout(pos_layout)
        taille_label = QLabel("Taille des cases")
        grid_layout.addWidget(taille_label)
        taille_spin = QSpinBox()
        grid_layout.addWidget(taille_spin)
        grid_box.setLayout(grid_layout)
        right_col.addWidget(grid_box)

        right_col.addSpacing(10)

        # Détails
        details_box = QGroupBox("Détails")
        details_box.setMinimumWidth(220)
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(10, 10, 10, 10)
        produit_label = QLabel("Produit : ...")
        details_layout.addWidget(produit_label)
        categorie_label = QLabel("Catégorie : ...")
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
        center_layout.addWidget(right_frame, stretch=0)

        main_layout.addLayout(center_layout)

        # Barre d'état
        self.status_bar = QLabel("Prêt")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_bar)

        # Récupérer le magasin du gérant
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT articles_json FROM shops WHERE user_id=?", (self.user_id,))
        result = c.fetchone()
        conn.close()
        if result and result[0]:
            self.afficher_stocks_depuis_json(result[0])
        else:
            self.status_bar.setText("Aucun article associé à ce magasin.")

    def ouvrir_fichier_json(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Fichiers JSON (*.json)")
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                self.afficher_stocks_depuis_json(filenames[0])
                self.status_bar.setText(f"Fichier chargé : {filenames[0]}")

    def afficher_stocks_depuis_json(self, articles_json_content):
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            # On reçoit le contenu JSON, pas un chemin
            data = json.loads(articles_json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    self.stocks_list.addItem(produit)
                    self.produit_categorie_map[produit] = categorie
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

    def afficher_details_produit(self, item):
        produit = item.text()
        categorie = self.produit_categorie_map.get(produit, "Inconnu")
        self.produit_label.setText(f"Produit : {produit}")
        self.categorie_label.setText(f"Catégorie : {categorie}")

    def filtrer_stocks(self, categorie):
        self.stocks_list.clear()
        if not hasattr(self, "produit_categorie_map"):
            return
        texte = self.search_input.text().lower() if hasattr(self, "search_input") else ""
        for produit, cat in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in produit.lower():
                self.stocks_list.addItem(produit)

    def deconnexion(self):
        from main import LoginWindow  
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def recuperer_magasins(self, user_id):
        """Exemple pour récupérer les magasins du gérant connecté (dans AdminWindow ou ailleurs)"""
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT * FROM shops WHERE user_id=?", (user_id,))
        shops = c.fetchall()
        conn.close()
        return shops

    def ouvrir_dialog_ajout_article(self):
        dialog = AddArticleDialog(self.categories, self)
        if dialog.exec():
            nom, categorie = dialog.get_data()
            if nom and categorie:
                # Ajoute l'article à la liste et à la map interne
                self.stocks_list.addItem(nom)
                self.produit_categorie_map[nom] = categorie
                self.categories.add(categorie)
                self.status_bar.setText(f"Article '{nom}' ajouté à la catégorie '{categorie}'.")
                self.filtre_combo.blockSignals(True)
                self.filtre_combo.clear()
                self.filtre_combo.addItem("Toutes les catégories")
                for cat in sorted(self.categories):
                    self.filtre_combo.addItem(cat)
                self.filtre_combo.blockSignals(False)

                # Récupère le chemin du fichier JSON associé au magasin
                conn = sqlite3.connect("market_tracer.db")
                c = conn.cursor()
                c.execute("SELECT articles_json FROM shops WHERE user_id=?", (self.user_id,))
                result = c.fetchone()
                conn.close()
                if result and result[0]:
                    chemin_json = result[0]
                    # Ajoute l'article au fichier JSON
                    try:
                        with open(chemin_json, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception:
                        data = {}
                    if categorie not in data:
                        data[categorie] = []
                    if nom not in data[categorie]:
                        data[categorie].append(nom)
                    with open(chemin_json, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

            else:
                QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

    def retirer_article_selectionne(self):
        item = self.stocks_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return
        nom = item.text()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setText(f"Voulez-vous vraiment retirer l'article '{nom}' du stock ?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply = msg_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            # Retire de la liste interne
            categorie = self.produit_categorie_map.get(nom)
            if categorie and nom in self.produit_categorie_map:
                del self.produit_categorie_map[nom]
            self.stocks_list.takeItem(self.stocks_list.row(item))
            # Mise à jour du JSON
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("SELECT articles_json FROM shops WHERE user_id=?", (self.user_id,))
            result = c.fetchone()
            conn.close()
            if result and result[0]:
                chemin_json = result[0]
                try:
                    with open(chemin_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
                # Retrait de l'article
                if categorie in data and nom in data[categorie]:
                    data[categorie].remove(nom)
                    if not data[categorie]:
                        del data[categorie]
                with open(chemin_json, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.afficher_stocks_depuis_json(chemin_json)
            self.status_bar.setText(f"Article '{nom}' retiré du stock.")

    def ouvrir_modifier_magasin(self):
        from createShopWindow import CreateShopWindow
        # Récupère les infos du magasin
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
            # Mettre à jour les stocks si nécessaire
            self.afficher_stocks_depuis_json(dialog.json_input.text())

    def rechercher_stocks(self, texte):
        texte = texte.lower()
        categorie = self.filtre_combo.currentText()
        self.stocks_list.clear()
        for produit, cat in self.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in produit.lower():
                self.stocks_list.addItem(produit)

    def ouvrir_gestion_employes(self):
        # Récupère le shop_id du gérant connecté
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

# ==============================================================
# Fenêtre de gestion des employés
# =============================================================

class EmployeeManagerDialog(QDialog):
    def __init__(self, shop_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gérer les employés")
        self.setMinimumWidth(400)
        self.shop_id = shop_id

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        layout.addWidget(self.list)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_edit = QPushButton("Modifier")
        self.btn_del = QPushButton("Supprimer")
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

        self.btn_add.clicked.connect(self.add_employee)
        self.btn_edit.clicked.connect(self.edit_employee)
        self.btn_del.clicked.connect(self.delete_employee)

        self.refresh()

    def refresh(self):
        self.list.clear()
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE role='Employé' AND shop_id=?", (self.shop_id,))
        for emp_id, username in c.fetchall():
            self.list.addItem(f"{emp_id} - {username}")
        conn.close()

    def add_employee(self):
        dialog = EmployeeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, role, shop_id) VALUES (?, ?, 'Employé', ?)", (username, password, self.shop_id))
            conn.commit()
            conn.close()
            self.refresh()

    def edit_employee(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un employé à modifier.")
            return
        emp_id = int(item.text().split(" - ")[0])
        dialog = EmployeeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, emp_id))
            conn.commit()
            conn.close()
            self.refresh()

    def delete_employee(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un employé à supprimer.")
            return
        emp_id = int(item.text().split(" - ")[0])
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet employé ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE id=?", (emp_id,))
            conn.commit()
            conn.close()
            self.refresh()

# ==============================================================
# Fenêtre de dialogue pour ajouter ou modifier un employé
# =============================================================

class EmployeeEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Employé")
        layout = QFormLayout(self)
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Nom d'utilisateur", self.user_input)
        layout.addRow("Mot de passe", self.pass_input)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        return self.user_input.text(), self.pass_input.text()
    
# ==============================================================
# Fonction pour détecter le thème sombre du système
# =============================================================

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
        # Linux (Gnome/GTK)
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