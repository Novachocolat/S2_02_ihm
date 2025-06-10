from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class EmployeeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenêtre Employé")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        label = QLabel("Bienvenue sur la fenêtre Employé !")
        layout.addWidget(label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeWindow()
    window.show()
    sys.exit(app.exec())