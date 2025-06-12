# ==============================================================
#
# Market Tracer - Boîte de dialogue d'édition d'employé
# Développé par Lysandre Pace--Boulnois
# Dernière modification : 12/06/2025
#
# ==============================================================

from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox

class EmployeeEditDialog(QDialog):
    # Constructeur de la boîte de dialogue d'édition d'employé
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

    # Retourne les données saisies par l'utilisateur (nom d'utilisateur et mot de passe)
    def get_data(self):
        return self.user_input.text(), self.pass_input.text()