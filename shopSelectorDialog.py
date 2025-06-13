import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox

class ShopSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choisir un magasin")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)

        btns = QHBoxLayout()
        self.btn_select = QPushButton("Ouvrir")
        self.btn_cancel = QPushButton("Annuler")
        btns.addWidget(self.btn_select)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_select.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        self.selected_shop_id = None
        self.populate_shops()

        self.list.itemDoubleClicked.connect(self.accept)

    def populate_shops(self):
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, nom FROM shops")
        for shop_id, nom in c.fetchall():
            self.list.addItem(f"{shop_id} - {nom}")
        conn.close()

    def accept(self):
        item = self.list.currentItem()
        if item:
            self.selected_shop_id = int(item.text().split(" - ")[0])
            super().accept()
        else:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un magasin.")