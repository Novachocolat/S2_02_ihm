import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QMessageBox
from employeeEditDialog import EmployeeEditDialog

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