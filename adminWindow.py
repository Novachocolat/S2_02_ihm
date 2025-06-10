# ==============================================================
# Market Tracer - Page gérant
# ==============================================================
# Importations
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QListWidget,
    QLineEdit, QCheckBox, QSpinBox, QGroupBox, QGridLayout, QMenuBar, QMenu, QFileDialog, QComboBox,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import sys
import json
import sqlite3
# ==============================================================
# Fenêtre d'ajout d'article

class AddArticleDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un article")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.setStyleSheet("background: #eee; color: #222; font-size: 12px;")
        self.setMinimumWidth(300)
        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.nom_input.setStyleSheet("color: #222; background: #fff;") 
        layout.addRow("Nom de l'article :", self.nom_input)

        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(sorted(categories) if categories else [])
        self.categorie_combo.setStyleSheet("color: #222; background: #fff;") 
        layout.addRow("Catégorie :", self.categorie_combo)

        for i in range(layout.rowCount()):
            label = layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label and label.widget():
                label.widget().setStyleSheet("color: #222; background: transparent;")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setStyleSheet("color: #222; background: #ddd;")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.nom_input.text(), self.categorie_combo.currentText()
# ==============================================================
# Fenêtre principale du gérant

class AdminWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
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

        # Gestion
        gestion_menu = menubar.addMenu("Gestion")
        action_modifier_magasin = gestion_menu.addAction("Modifier mon magasin")
        action_modifier_magasin.triggered.connect(self.ouvrir_modifier_magasin)

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

        # Boutons stock
        btn_ajouter = QPushButton("Ajouter à mon stock")
        btn_ajouter.setStyleSheet("background: #4be39a; color: #222; font-weight: bold; min-height: 32px;")
        btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout_article)
        btn_retirer = QPushButton("Retirer de mon stock")
        btn_retirer.setStyleSheet("background: #ff3c2f; color: #222; font-weight: bold; min-height: 32px;")
        btn_retirer.clicked.connect(self.retirer_article_selectionne)
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
        left_col.addWidget(self.stocks_list, stretch=1)  # Ajoute stretch ici

        self.stocks_list.itemClicked.connect(self.afficher_details_produit)
        self.produit_categorie_map = {}

        left_col.addStretch()  # Laisse ce stretch après la liste
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

        # Récupérer le magasin du gérant
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT articles_json FROM shops WHERE user_id=?", (self.user_id,))
        result = c.fetchone()
        conn.close()
        if result and result[0]:
            self.afficher_stocks_depuis_json(result[0])
        else:
            self.status_bar.setText("Aucun fichier d'articles associé à ce magasin.")

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
        msg_box.setStyleSheet("""
            QLabel { color: #222; }
            QPushButton { color: #222; }
            QMessageBox { background: #fff; }
        """)
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

# ==============================================================
# Lancement de l'application
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())