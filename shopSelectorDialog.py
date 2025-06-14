# ==============================================================
# Dialog de sélection d'un magasin
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox
)

class ShopSelectorDialog(QDialog):
    """Boîte de dialogue pour sélectionner un magasin à ouvrir."""
    def __init__(self, parent=None):
        """Initialise la boîte de dialogue pour sélectionner un magasin."""
        super().__init__(parent)
        self.setWindowTitle("Choisir un magasin")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Création des boutons pour ouvrir ou annuler la sélection
        btns = QHBoxLayout()
        self.btn_select = QPushButton("Ouvrir")
        self.btn_cancel = QPushButton("Annuler")
        btns.addWidget(self.btn_select)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        # Connexion des boutons aux méthodes correspondantes
        self.btn_select.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        # Initialisation de la liste des magasins et de l'identifiant sélectionné
        self.selected_shop_id = None
        self.populate_shops()

        self.list.itemDoubleClicked.connect(self.accept)

    def populate_shops(self):
        """Remplit la liste des magasins depuis la base de données."""
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, nom FROM shops")
        for shop_id, nom in c.fetchall():
            self.list.addItem(f"{shop_id} - {nom}")
        conn.close()

    def accept(self):
        """Valide la sélection du magasin."""
        item = self.list.currentItem()
        if item:
            self.selected_shop_id = int(item.text().split(" - ")[0])
            super().accept()
        else:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un magasin.")