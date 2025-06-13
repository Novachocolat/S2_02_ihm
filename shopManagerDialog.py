# ==============================================================
#
# Market Tracer - Boîte de gestion des magasins
# Développé par Lysandre Pace--Boulnois
# Dernière modification : 12/06/2025
#
# ==============================================================

# Importations
import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QMessageBox

# ==============================================================
# Boîte de dialogue pour la gestion des magasins
# ==============================================================
class ShopManagerDialog(QDialog):
    # Constructeur de la boîte de gestion des magasins
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mes magasins")
        self.setMinimumWidth(400)
        self.user_id = user_id

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)

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

        self.btn_create.clicked.connect(self.create_shop)
        self.btn_load.clicked.connect(self.load_shop)
        self.btn_edit.clicked.connect(self.edit_shop)
        self.btn_del.clicked.connect(self.delete_shop)

        self.refresh()

    # Rafraîchit la liste des magasins
    def refresh(self):
        self.list.clear()
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, nom FROM shops WHERE user_id=?", (self.user_id,))
        for shop_id, nom in c.fetchall():
            self.list.addItem(f"{shop_id} - {nom}")
        conn.close()

    # Récupère l'identifiant du magasin sélectionné
    def get_selected_shop_id(self):
        item = self.list.currentItem()
        if not item:
            return None
        return int(item.text().split(" - ")[0])

    # Crée un nouveau magasin
    def create_shop(self):
        from createShopWindow import CreateShopWindow
        dlg = CreateShopWindow(self.user_id, self)
        dlg.exec()
        self.refresh()

    # Charge le magasin sélectionné
    def load_shop(self):
        shop_id = self.get_selected_shop_id()
        if shop_id:
            self.accept()
            self.selected_shop_id = shop_id

    # Modifie le magasin sélectionné
    def edit_shop(self):
        shop_id = self.get_selected_shop_id()
        if shop_id:
            from createShopWindow import CreateShopWindow
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
                dlg = CreateShopWindow(self.user_id, self, shop_data)
                dlg.exec()
                self.refresh()

    # Supprime le magasin sélectionné
    def delete_shop(self):
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