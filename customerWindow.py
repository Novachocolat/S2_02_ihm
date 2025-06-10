from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class CustomerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenêtre Client")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        label = QLabel("Bienvenue sur la fenêtre Client !")
        layout.addWidget(label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomerWindow()
    window.show()
    sys.exit(app.exec())