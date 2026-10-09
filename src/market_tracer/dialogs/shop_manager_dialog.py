# ==============================================================
# Dialog de gestion des magasins
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QPushButton, QVBoxLayout
)

from market_tracer.dialogs.configure_window import ConfigureWindow
from market_tracer.models import shop_model
from market_tracer.ui_helpers import ask_yes_no, list_entry, list_entry_id


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
        for shop_id, nom in shop_model.list_shops(self.user_id):
            self.list.addItem(list_entry(shop_id, nom))

    def get_selected_shop_id(self):
        """Retourne l'ID du magasin sélectionné dans la liste."""
        item = self.list.currentItem()
        if not item:
            return None
        return list_entry_id(item.text())

    def create_shop(self):
        """Ouvre une fenêtre pour créer un nouveau magasin."""
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
        if shop_id and shop_model.shop_exists(shop_id):
            dlg = ConfigureWindow(self.user_id, self)
            dlg.exec()
            self.refresh()

    def delete_shop(self):
        """Supprime le magasin sélectionné après confirmation."""
        shop_id = self.get_selected_shop_id()
        if shop_id:
            if ask_yes_no(self, "Confirmation", "Supprimer ce magasin ?"):
                shop_model.delete_shop(shop_id)
                self.refresh()
