# ==============================================================
# Dialogue pour ajouter un article
# Développé par L. PACE--BOULNOIS, D. MELOCCO
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QComboBox, QFormLayout, QDialogButtonBox
)
from PyQt6.QtGui import QIcon

class AddArticleDialog(QDialog):
    """Boîte de dialogue pour ajouter un article."""
    def __init__(self, categories, parent=None):
        """Initialisation de la boîte de dialogue d'ajout d'article.

        Args:
            categories (list): liste des catégories disponibles.
            parent (QWidget, optional): widget parent de la boîte de dialogue.
        """
        super().__init__(parent)
        self.setWindowTitle("Ajouter un article")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(300, 100)
        layout = QFormLayout(self)

        # Création du champ de saisie pour le nom de l'article
        self.nom_input = QLineEdit()
        layout.addRow("Nom de l'article :", self.nom_input)

        # Création de la liste déroulante pour les catégories
        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(sorted(categories) if categories else [])
        layout.addRow("Catégorie :", self.categorie_combo)

        # Boutons OK et Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Récupère les données saisies dans la boîte de dialogue.

        Returns:
            tuple: nom de l'article et catégorie sélectionnée.
        """
        return self.nom_input.text(), self.categorie_combo.currentText()