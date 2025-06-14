# ==============================================================
# Dialogue d'édition d'employé
# Développé par L. PACE--BOULNOIS
# Dernière modification : 14/06/2025
# ==============================================================

from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox

class EmployeEditDialog(QDialog):
    """Boîte de dialogue pour éditer les informations d'un employé."""
    def __init__(self, parent=None):
        """Initialise la boîte de dialogue avec les champs pour le nom d'utilisateur et le mot de passe."""
        super().__init__(parent)
        self.setWindowTitle("Employé")
        layout = QFormLayout(self)
        
        # Création des champs pour le nom d'utilisateur et le mot de passe
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Nom d'utilisateur", self.user_input)
        layout.addRow("Mot de passe", self.pass_input)
        
        # Création des boutons OK et Annuler
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        """Retourne les données saisies par l'utilisateur."""
        return self.user_input.text(), self.pass_input.text()