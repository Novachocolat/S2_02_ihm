# ==============================================================
# Dialog de gestion des magasins
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QMessageBox
)

class ShopManagerDialog(QDialog):
    """Boîte de dialogue pour gérer les magasins de l'utilisateur."""
    def __init__(self, user_id, parent=None):
        """Initialise la boîte de dialogue pour gérer les magasins."""
        super().__init__(parent)
        self.setWindowTitle("Mes magasins")
        self.setFixedSize(400, 300)
        self.user_id = user_id

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Création des boutons pour gérer les magasins
        btns = QHBoxLayout()
        self.btn_create = QPushButton("Créer")
        self.btn_load = QPushButton("Charger")
        self.btn_edit = QPushButton("Modifier")
        self.btn_del = QPushButton("Supprimer")
        btns.addWidget(self.btn_create)
        btns.addWidget(self.btn_load)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

        # Connexion des boutons aux méthodes correspondantes
        self.btn_create.clicked.connect(self.create_shop)
        self.btn_load.clicked.connect(self.load_shop)
        self.btn_edit.clicked.connect(self.edit_shop)
        self.btn_del.clicked.connect(self.delete_shop)

        self.refresh()

    def refresh(self):
        """Rafraîchit la liste des magasins de l'utilisateur."""
        self.list.clear()
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, nom FROM shops WHERE user_id=?", (self.user_id,))
        for shop_id, nom in c.fetchall():
            self.list.addItem(f"{shop_id} - {nom}")
        conn.close()

    def get_selected_shop_id(self):
        """Retourne l'ID du magasin sélectionné dans la liste."""
        item = self.list.currentItem()
        if not item:
            return None
        return int(item.text().split(" - ")[0])

    def create_shop(self):
        """Ouvre une fenêtre pour créer un nouveau magasin."""
        from configureWindow import ConfigureWindow
        dlg = ConfigureWindow(self.user_id, self)
        dlg.exec()
        self.refresh()

    def load_shop(self):
        """Charge le magasin sélectionné et ferme la boîte de dialogue."""
        shop_id = self.get_selected_shop_id()
        if shop_id:
            self.accept()
            self.selected_shop_id = shop_id

    def edit_shop(self):
        """Ouvre une fenêtre pour modifier le magasin sélectionné."""
        shop_id = self.get_selected_shop_id()
        if shop_id:
            from configureWindow import ConfigureWindow
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("SELECT nom, auteur, date_creation, apropos, chemin, articles_json FROM shops WHERE id=?", (shop_id,))
            row = c.fetchone()
            conn.close()
            if row:
                shop_data = {
                    "nom": row[0],
                    "auteur": row[1],
                    "date_creation": row[2],
                    "apropos": row[3],
                    "chemin": row[4],
                    "articles_json": row[5]
                }
                dlg = ConfigureWindow(self.user_id, self)
                dlg.exec()
                self.refresh()

    def delete_shop(self):
        """Supprime le magasin sélectionné après confirmation."""
        shop_id = self.get_selected_shop_id()
        if shop_id:
            reply = QMessageBox.question(self, "Confirmation", "Supprimer ce magasin ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                conn = sqlite3.connect("market_tracer.db")
                c = conn.cursor()
                c.execute("DELETE FROM shops WHERE id=?", (shop_id,))
                conn.commit()
                conn.close()
                self.refresh()