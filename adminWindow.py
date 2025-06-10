from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenêtre Admin")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        label = QLabel("Bienvenue sur la fenêtre Admin !")
        layout.addWidget(label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())