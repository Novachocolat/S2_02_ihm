from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

class CreateShopWindow(QWidget):
    def __init__(self, on_finish):
        super().__init__()
        self.setWindowTitle("Créer un magasin")
        self.setMinimumSize(900, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Ici, l'interface de création du magasin (à compléter)"))
        btn = QPushButton("Créer (continuer)")
        btn.clicked.connect(self.finish)
        layout.addWidget(btn)
        self.on_finish = on_finish

    def finish(self):
        self.on_finish()
        self.close()