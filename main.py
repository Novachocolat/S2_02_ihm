# ==============================================================

# Market Tracer - Page de connexion
# Développée par L. Pace--Boulnois et D. Melocco
# Dernière modification : 12/06/2025

# ==============================================================

# Importations
import sys
import random as rand
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
from adminWindow import AdminWindow
from employeeWindow import EmployeeWindow
from customerWindow import CustomerWindow
from createShopWindow import CreateShopWindow
from shopSelectorDialog import ShopSelectorDialog

# ==============================================================
# Création de la base de données et des tables

def init_db():
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                shop_id INTEGER,
                first_login INTEGER DEFAULT 1
            )
        ''')
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                auteur TEXT,
                date_creation TEXT,
                apropos TEXT,
                chemin TEXT,
                articles_json TEXT,
                user_id INTEGER,
                plan_json TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        # Ajout des colonnes si besoin (migration)
        for col, typ in [
            ("plan_json", "TEXT"),
            ("articles_json", "TEXT"),
            ("user_id", "INTEGER"),
            ("plan_image", "BLOB")
        ]:
            try:
                c.execute(f"ALTER TABLE shops ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError:
                pass
        # Ajout d'utilisateurs de test
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('gerant', '1234', 'Gérant')")
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('employe', 'abcd', 'Employé')")
        conn.commit()

# ==============================================================
# Page de connexion

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Connexion")
        self.setWindowIcon(QIcon("img/chariot.png"))
        self.setFixedSize(800, 600)
        self.selected_role = "Gérant"
        self.rand_banner = rand.randrange(1, 6)
        self.setup_ui()

    # Initialise l'interface utilisateur de la fenêtre de connexion
    def setup_ui(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        left_frame = QFrame()

        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo + titre
        logo_label = QLabel()
        logo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #222; margin-bottom: 10px;")
        left_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Connexion titre
        title = QLabel("Connexion")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("margin-top: 40px; margin-bottom: 20px;")
        left_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Boutons rôle
        role_layout = QHBoxLayout()
        self.role_buttons = {}
        for role in ["Gérant", "Employé", "Client"]:
            btn = QPushButton(role)
            btn.setCheckable(True)
            btn.setMaximumWidth(110)
            btn.setStyleSheet("""
                QPushButton {
                    background: #4be39a;
                    color: #222;
                    border-radius: 6px;
                    min-width: 100px;
                    min-height: 36px;
                    font-size: 16px;
                }
                QPushButton:checked {
                    border: 2px solid #222;
                    background: #111;
                    color: #fff;
                }
            """)
            btn.clicked.connect(lambda checked, r=role: self.select_role(r))
            self.role_buttons[role] = btn
            role_layout.addWidget(btn)
        self.role_buttons["Gérant"].setChecked(True)
        left_layout.addLayout(role_layout, stretch=0)
        left_layout.setAlignment(role_layout, Qt.AlignmentFlag.AlignHCenter)
        left_layout.addSpacing(20)

        # Formulaire
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        # Nom d'utilisateur
        self.user_label = QLabel("Nom d'utilisateur")
        self.user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_input = QLineEdit()
        self.user_input.setMaximumWidth(310)
        self.user_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.user_input.setStyleSheet("background: #bdbdbd; border-radius: 4px; padding: 6px; color: #222;")
        # Mot de passe
        self.pass_label = QLabel("Mot de passe")
        self.pass_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.pass_input = QLineEdit()
        self.pass_input.setMaximumWidth(310)
        self.pass_input.setPlaceholderText("Entrez votre mot-de-passe")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background: #bdbdbd; border-radius: 4px; padding: 6px; color: #222;")
        # Ajout au layout
        form_layout.addWidget(self.user_label, 0, 0)
        form_layout.addWidget(self.user_input, 1, 0)
        form_layout.addWidget(self.pass_label, 2, 0)
        form_layout.addWidget(self.pass_input, 3, 0)
        left_layout.addLayout(form_layout)
        left_layout.addSpacing(20)

        # Bouton connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #bdbdbd;
                color: #222;
                border-radius: 4px;
                min-height: 36px;
                font-size: 18px;
            }
            QPushButton:pressed {
                background: #888;
            }
        """)
        self.login_btn.clicked.connect(self.try_login)
        self.pass_input.returnPressed.connect(self.try_login)
        left_layout.addWidget(self.login_btn)
        self.enter_btn = QPushButton("Ouvrir une session")
        self.enter_btn.setStyleSheet("""
            QPushButton {
                background: #bdbdbd;
                color: #222;
                border-radius: 4px;
                min-height: 36px;
                font-size: 18px;
            }
            QPushButton:pressed {
                background: #888;
            }
        """)
        self.enter_btn.clicked.connect(self.enter_as_client)
        self.enter_btn.hide()
        left_layout.addWidget(self.enter_btn)
        left_layout.addSpacing(40)

        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        left_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Footer
        footer= QLabel("Powered by Place Holder")
        footer.setStyleSheet("color: #888; font-size: 12px; margin-top: 40px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(footer)

        # Partie droite (image)
        right_frame = QFrame()
        right_frame.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label = QLabel()
        pixmap = QPixmap(f"img/mt_banner_{self.rand_banner}.png")
        pixmap = pixmap.scaled(300, 580, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(img_label)

        # Ajout au layout principal
        main_layout.addWidget(left_frame, stretch=3)
        main_layout.addWidget(right_frame, stretch=2)

    # Gère la sélection du rôle
    def select_role(self, role):
        self.selected_role = role
        for r, btn in self.role_buttons.items():
            btn.setChecked(r == role)
        if role == "Client":
            self.login_btn.hide()
            self.enter_btn.show()
            self.user_label.hide()
            self.user_input.hide()
            self.pass_label.hide()
            self.pass_input.hide()
        else:
            self.login_btn.show()
            self.enter_btn.hide()
            self.user_label.show()
            self.user_input.show()
            self.pass_label.show()
            self.pass_input.show()

    # Connecte l'utilisateur
    def try_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        role = self.selected_role
        with sqlite3.connect("market_tracer.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (username, password, role))
            user = c.fetchone()
            if user:
                if role == "Gérant":
                    user_id, _, _, _, _, first_login = user
                    if first_login:
                        self.create_shop_window = CreateShopWindow(user_id, parent=self)
                        self.create_shop_window.exec()
                        self.open_admin_window(user_id)
                        c.execute("UPDATE users SET first_login=0 WHERE id=?", (user_id,))
                        conn.commit()
                    else:
                        self.open_admin_window(user_id)
                elif role == "Employé":
                    shop_id = user[4]
                    if shop_id:
                        c.execute("SELECT articles_json, chemin FROM shops WHERE id=?", (shop_id,))
                        shop_info = c.fetchone()
                        if shop_info:
                            articles_json, plan_path = shop_info
                            self.employee_window = EmployeeWindow(articles_json, plan_path)
                            self.employee_window.show()
                            self.close()
                        else:
                            QMessageBox.warning(self, "Erreur", "Aucun magasin associé à ce compte employé.")
                    else:
                        QMessageBox.warning(self, "Erreur", "Aucun magasin associé à ce compte employé.")
                self.close()
            else:
                self.error_label.setText("Nom d'utilisateur, mot de passe ou rôle incorrect.")

    # Lance la fenêtre client
    def enter_as_client(self):
        self.open_client_window()
        self.close()

    # Ouvre la fenêtre de sélection de magasin pour le client
    def open_client_window(self):
        with sqlite3.connect("market_tracer.db") as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM shops")
            nb_shops = c.fetchone()[0]
            if nb_shops == 0:
                QMessageBox.warning(self, "Aucun magasin", "Aucun magasin n'est disponible pour les clients.")
                return
        dlg = ShopSelectorDialog(self)
        if dlg.exec() and dlg.selected_shop_id:
            shop_id = dlg.selected_shop_id
            with sqlite3.connect("market_tracer.db") as conn:
                c = conn.cursor()
                c.execute("SELECT articles_json FROM shops WHERE id=?", (shop_id,))
                result = c.fetchone()
                articles_json = result[0] if result else None
            self.client_window = CustomerWindow(articles_json, shop_id)
            self.client_window.show()

    # Ouvre la fenêtre d'administration pour le gérant
    def open_admin_window(self, user_id):
        self.admin_window = AdminWindow(user_id)
        self.admin_window.show()

    # Ouvre la fenêtre employé
    def open_employee_window(self):
        self.employee_window = EmployeeWindow()
        self.employee_window.show()


# ==============================================================
# Mise en route de l'application
# ==============================================================
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())