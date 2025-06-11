from PyQt6.QtWidgets import QDialog, QLineEdit, QComboBox, QFormLayout, QDialogButtonBox
from PyQt6.QtGui import QIcon

class AddArticleDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un article")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.setMinimumWidth(300)
        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        layout.addRow("Nom de l'article :", self.nom_input)

        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(sorted(categories) if categories else [])
        layout.addRow("Catégorie :", self.categorie_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.nom_input.text(), self.categorie_combo.currentText()