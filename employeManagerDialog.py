# ==============================================================
# Dialogue de gestion des employés
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QMessageBox
from employeEditDialog import EmployeEditDialog

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
        conn = sqlite3.connect("market_tracer.db")
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE role='Employé' AND shop_id=?", (self.shop_id,))
        for emp_id, username in c.fetchall():
            self.list.addItem(f"{emp_id} - {username}")
        conn.close()

    def add_employee(self):
        """Ajoute un nouvel employé à la boutique."""
        dialog = EmployeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, role, shop_id) VALUES (?, ?, 'Employé', ?)", (username, password, self.shop_id))
            conn.commit()
            conn.close()
            self.refresh()

    def edit_employee(self):
        """Modifie les informations de l'employé sélectionné."""
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un employé à modifier.")
            return
        emp_id = int(item.text().split(" - ")[0])
        dialog = EmployeEditDialog(parent=self)
        if dialog.exec():
            username, password = dialog.get_data()
            conn = sqlite3.connect("market_tracer.db")
            c = conn.cursor()
            c.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, emp_id))
            conn.commit()
            conn.close()
            self.refresh()

    def delete_employee(self):
        """Supprime l'employé sélectionné de la boutique."""
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