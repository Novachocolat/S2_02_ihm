# ==============================================================
# Dialogue de gestion des employés
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QMessageBox, QPushButton, QVBoxLayout
)

from market_tracer.dialogs.employe_edit_dialog import EmployeEditDialog
from market_tracer.models import employee_model
from market_tracer.ui_helpers import ask_yes_no, list_entry, list_entry_id


class EmployeManagerDialog(QDialog):
    """Boîte de dialogue pour gérer les employés d'une boutique."""
    def __init__(self, shop_id, parent=None):
        """Initialise la boîte de dialogue pour gérer les employés d'une boutique."""
        super().__init__(parent)
        self.setWindowTitle("Gérer les employés")
        self.setMinimumWidth(400)
        self.shop_id = shop_id

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        layout.addWidget(self.list)

        # Création des boutons pour ajouter, modifier et supprimer des employés
        btns = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_edit = QPushButton("Modifier")
        self.btn_del = QPushButton("Supprimer")
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

        # Connexion des boutons aux méthodes correspondantes
        self.btn_add.clicked.connect(self.add_employee)
        self.btn_edit.clicked.connect(self.edit_employee)
        self.btn_del.clicked.connect(self.delete_employee)

        self.refresh()

    def refresh(self):
        """Rafraîchit la liste des employés de la boutique."""
        self.list.clear()
        for emp_id, username in employee_model.list_employees(self.shop_id):
            self.list.addItem(list_entry(emp_id, username))

    def add_employee(self):
        """Ajoute un nouvel employé à la boutique."""
        dialog = EmployeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            employee_model.add_employee(self.shop_id, username, password)
            self.refresh()

    def edit_employee(self):
        """Modifie les informations de l'employé sélectionné."""
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un employé à modifier.")
            return
        emp_id = list_entry_id(item.text())
        dialog = EmployeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            employee_model.update_employee(emp_id, username, password)
            self.refresh()

    def delete_employee(self):
        """Supprime l'employé sélectionné de la boutique."""
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un employé à supprimer.")
            return
        emp_id = list_entry_id(item.text())
        if ask_yes_no(self, "Confirmation", "Supprimer cet employé ?"):
            employee_model.delete_employee(emp_id)
            self.refresh()
